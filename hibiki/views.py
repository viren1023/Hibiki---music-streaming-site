import json
import random
import threading
import ast
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from ytmusicapi import YTMusic
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.cache import cache
from django.views.decorators.http import require_POST
from .models import User, Playlist
import yt_dlp
from django.http import HttpResponse, JsonResponse
from .forms import RegisterForm, LoginForm
from datetime import date, timedelta
from .forms import FeedbackForm
from .core_logic.fetchmetadata import home_metadata, similar_search_metadata, similar_songs_name, playlist_metadata, fetch_audio_metadata,generate_radio_playlist
from django.contrib import messages
from .models import Report,Feedback,User,SongPlay
from django.db.models import Sum


ytmusic = YTMusic()

def set_cookie(key, value, max_age=None):
    response = HttpResponse()
    response.set_cookie(key, value, max_age=max_age, secure=True)
    return response

def landing_view(request):
    # Check if cookie exists
    if request.COOKIES.get("HIBIKI_USERNAME"):
        # If logged in, redirect to home
        return redirect("home")
    else:
        # Otherwise, show landing page
        return render(request, "landing.html")

def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            
            if(username=="admin" and password=="admin@123"):
                return redirect("analytics_dashboard")
            else:
                try:
                    user = User.objects.get(username=username, password=password)
                except User.DoesNotExist:
                    messages.error(request, "Invalid username or password")
                    return redirect("login")
                
                # Update Last Login
                user.last_login = timezone.now()
                user.save()

                response = redirect("home")
                response.set_cookie(
                    key="HIBIKI_USERNAME",
                    value=user.username,
                    secure=False,  # set True if HTTPS
                    max_age=86400
                )
                return response
    else:
        form = LoginForm()

    return render(request, "login.html", {"form": form})

def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()  # direct save since no hashing
            
            user.last_login = timezone.now()
            user.save()
            
            response = redirect("home")
            response.set_cookie(
                key="HIBIKI_USERNAME",
                value=user.username,
                secure=False,   # set True if using HTTPS
                max_age=86400
            )
            return response
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = RegisterForm()

    return render(request, "register.html", {"form": form})

def home(request):
    # fetch data from YTMusic
    result = home_metadata()
    result_key=list(result.keys())
    username = request.COOKIES.get('HIBIKI_USERNAME', 'Guest User')
    
    get_item_type = lambda item: (
        "song" if item.get("videoId") 
        else "playlist" if item.get("playlistId")
        else "album" if item.get("audioPlaylistId") 
        else None
    )

    print(get_item_type)
    # playlists -> from "Trending community playlists"
    section1 = []
    for item in result.get(f"{result_key[1]}", [])[:4]:
        item_type = get_item_type(item)
        print("Section1 item type:", item_type) 
        section1.append({
            "title": item.get("title"),
            "tag": item.get("description", ""),
            "id": item.get("videoId") or item.get("playlistId") or item.get("audioPlaylistId"),
            "type" : get_item_type(item),
            "img": item["thumbnails"][0]["url"] if item.get("thumbnails") else "https://picsum.photos/400/250?random="+f"{random.randint(1,1000)}"
        })

    # recommendations -> from "Albums for you"
    section2 = []
    for item in result.get(f"{result_key[2]}", [])[:3]:
        item_type = get_item_type(item)
        print("Section2 item type:", item_type) 
        section2.append({
            "title": item.get("title"),
            "tag": item.get("type", "Album"),
            "id": item.get("videoId") or item.get("playlistId") or item.get("audioPlaylistId"),
            "type" : get_item_type(item),
            "img": item["thumbnails"][0]["url"] if item.get("thumbnails") else "https://picsum.photos/400/250?random="+f"{random.randint(1,1000)}"
        })

    # popular songs -> from "Quick picks"
    section3 = []
    for item in result.get(f"{result_key[0]}", [])[:12]:
        item_type = get_item_type(item)
        print("Section3 item type:", item_type) 
        section3.append({
            "title": item.get("title"),
            "artist": ", ".join([artist["name"] for artist in item.get("artists", [])]),
            "id": item.get("videoId") or item.get("playlistId") or item.get("audioPlaylistId"),
            "type" : get_item_type(item),
            "img": item["thumbnails"][0]["url"] if item.get("thumbnails") else "https://picsum.photos/400/250?random="+f"{random.randint(1,1000)}"
        })

    context = {
        "username": username,
        "title":result_key,
        "section1": section1,
        "section2": section2,
        "section3": section3,
    }
    return render(request, "home.html", context)






# def search_page(request):
#     query = ""
#     if request.method == "POST":
#         query = request.POST.get("search_text", "")
#         # similar_songs = similar_songs_name(query)
#         # print(similar_songs)        
#         # print(query)
#     # similar_search_metadata(query)
#     return render(request, "search.html", {"query": query})

# def similar_name(request):
#     print("hi")
#     query = request.GET.get('q', '')
#     matching_songs = similar_songs_name(query)
#     print(matching_songs)
#     return JsonResponse(matching_songs, safe=False)



# Suggestions (autocomplete)
def similar_songs_name(query):
    if len(query) >= 3:
        return ytmusic.get_search_suggestions(query)
    return []

def similar_name(request):
    query = request.GET.get('q', '')
    matching_songs = similar_songs_name(query)
    return JsonResponse(matching_songs, safe=False)

# Search results page
def search_page(request):
    query = ""
    search_results = []
    mood_categories = []
    charts = {}

    if request.method == "POST":
        query = request.POST.get("search_text", "").strip()
        if query:
            results = ytmusic.search(query,filter="songs" )
            search_results = results[:10]
            print(search_results)
            # print(results[0])
            return render(request, "search.html", {
                "query": query,
                "results": search_results,
                "mood_categories": mood_categories,
                "charts": charts
            })
    else:
        # No query yet → show moods + charts
        mood_categories = ytmusic.get_mood_categories()
        charts = ytmusic.get_charts(country="ZZ")
        if(not charts):
            charts = ytmusic.get_charts()
            pass  # You can change country
        return render(request, "search.html", {
            "query": query,
            "results": search_results,
            "mood_categories": mood_categories["Moods & moments"] ,
            "charts": charts["videos"] 
        })
    


# def fetch_audio(request):
#     name = request.GET.get("name")
#     if not name:
#         return JsonResponse({"error": "No song name provided"}, status=400)
#     pass

def playlist_view(request):
    playlistId = request.GET.get("id", "")
    user_playlist_id=request.GET.get("upid", "")
    
    if(playlistId):
        playlist = playlist_metadata(playlistId)
        context = {
            "playlist": playlist,
            "tracks": playlist["tracks"],
        }
    if(user_playlist_id):
        playlist = Playlist.objects.filter(id=user_playlist_id).first()
        context = {
            "playlist": playlist,
            "tracks": playlist.tracks,
        }
    return render(request, "playlist.html",context)

# def playlist_view(request):
#     playlistId = request.GET.get("id", "")
#     playlist = playlist_metadata(playlistId)
        
#     context = {
#         "playlist": playlist,
#         "tracks": playlist["tracks"],
#     }
#     return render(request, "playlist.html", context)


def player_api(request):
    song_id = request.GET.get("songId")
    playlist_id = request.GET.get("playlistId")
    upid=request.GET.get("upid")

    if playlist_id:
        playlist = playlist_metadata(playlist_id)
        tracks = playlist.get("tracks", [])
    elif song_id:
        playlist = generate_radio_playlist(song_id)
        tracks = playlist.get("tracks", [])
    elif upid:
        playlist = Playlist.objects.filter(id=upid).first()
        tracks=playlist.tracks
        playlist = {
            "id": playlist.id,
            "title": playlist.title,
            "user_id": playlist.user.id,
            "tracks": playlist.tracks,  # already a list of dicts
            "created_at": playlist.created_at.isoformat()  # convert datetime to string
        }
    else:
        return JsonResponse({"error": "No song or playlist provided"}, status=400)
    
    # print(f"Tracks: {tracks}")
    # print(f"Playlist: {playlist}")
    
    # Pre-cache all audio URLs in background
    # precache_audio_urls(tracks)

    return JsonResponse({
        "playlist": playlist,
        "tracks": tracks
    })

def get_audio_url(request):
    video_id = request.GET.get("video_id")
    if not video_id:
        return JsonResponse({"error": "No video_id provided"}, status=400)
    
    username = request.COOKIES.get("HIBIKI_USERNAME")

    # Check cache first
    cached_url = cache.get(video_id)
    if cached_url:
        log_song_play(username, video_id)
        return JsonResponse({"audio_url": cached_url})

    video_url = f"https://music.youtube.com/watch?v={video_id}"
    ydl_opts = {
        "format": "bestaudio/best",
        "quiet": True,
        "skip_download": True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            audio_url = info.get("url")
            if audio_url:
                # store in cache for 1 day (86400 seconds)
                cache.set(video_id, audio_url, timeout=86400)
                log_song_play(username, video_id)
                return JsonResponse({"audio_url": audio_url})
            else:
                return JsonResponse({"error": "Failed to extract audio URL"}, status=500)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    
def log_song_play(username, song_id):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        user = None 
    
    audio_data = fetch_audio_metadata(song_id)
    duration = audio_data["duration"]
    SongPlay.objects.create(
        user=user,            # can be None for guest
        song_id=song_id,
        duration=duration,
        played_at=timezone.now()
    )

def get_all_from_cache():
    pass
    

def moods_view(request):
    mood_id = request.GET.get("id")
    playlists = ytmusic.get_mood_playlists(mood_id)
    
    return render(request, "moods.html", {"playlists": playlists})

def user_playlist(request):
    username = request.COOKIES.get("HIBIKI_USERNAME")
    if not username:
        playlists = Playlist.objects.none()  # no user, return empty queryset
    else:
        try:
            user = User.objects.get(username=username)
            playlists = Playlist.objects.filter(user=user).order_by('-created_at')
        except User.DoesNotExist:
            playlists = Playlist.objects.none()

    return render(request, "myPlaylist.html", {"playlists": playlists})


@require_POST
def create_playlist(request):
    name = request.POST.get("name", "").strip()
    username = request.COOKIES.get("HIBIKI_USERNAME")
    
    if not username:
            # No user found in cookie
            return redirect("login")
        
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        # If user not found, prevent creating playlist
        return redirect("login")
    

    if name:
        Playlist.objects.create(title=name, user=user)  # set user_id appropriately
    return redirect("myPlaylist")

@require_POST
def delete_playlist(request, pk):
    playlist = get_object_or_404(Playlist, pk=pk)
    playlist.delete()
    return redirect("myPlaylist")

# ================== CACHE  ==================
# def precache_audio_urls(tracks):
#     def fetch_audio(track):
#         video_id = track.get("videoId")
#         if not video_id:
#             return
#         if cache.get(video_id):
#             return  # already cached
#         video_url = f"https://music.youtube.com/watch?v={video_id}"
#         ydl_opts = {"format": "bestaudio/best", "quiet": True, "skip_download": True}
#         try:
#             with yt_dlp.YoutubeDL(ydl_opts) as ydl:
#                 info = ydl.extract_info(video_url, download=False)
#                 audio_url = info.get("url")
#                 if audio_url:
#                     cache.set(video_id, audio_url, timeout=86400)  # 1 day
#         except Exception as e:
#             print(f"Failed to cache {video_id}: {e}")

#     # Start a thread for each track (or limit to 1 thread per playlist if many)
#     for track in tracks:
#         threading.Thread(target=fetch_audio, args=(track,), daemon=True).start()
        
def precache_audio_urls(request):
    print("In cache process...")
    try:
        data = json.loads(request.body)
        ids = data.get("video_ids", [])
    except Exception:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    
    def worker():
        for video_id in ids:
            print(video_id)
            if not video_id or cache.get(video_id):
                continue
            video_url = f"https://music.youtube.com/watch?v={video_id}"
            ydl_opts = {"format": "bestaudio/best", "quiet": True, "skip_download": True}
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(video_url, download=False)
                    audio_url = info.get("url")
                    if audio_url:
                        cache.set(video_id, audio_url, timeout=86400)
            except Exception as e:
                print(f"Failed to cache {video_id}: {e}")

    # Launch a single background thread that caches all songs
    threading.Thread(target=worker, daemon=True).start()
    print("Cacheing done.")
    return JsonResponse({"status": "Caching started", "count": len(ids)})


def show_playlist(request):
    username = request.COOKIES.get("HIBIKI_USERNAME")
    playlists_data = []

    if username:
        try:
            user = User.objects.get(username=username)
            playlists = Playlist.objects.filter(user=user).order_by('-created_at')
            playlists_data = [{"id": p.id, "name": p.title, "tracksLength": len(p.tracks)} for p in playlists]
        except User.DoesNotExist:
            pass
    return JsonResponse({"playlists": playlists_data})

@csrf_exempt
def add_to_playlist(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            playlist_id = data.get("playlist_id")
            track_str = str(data.get("track"))
            print(track_str)
            my_dict = ast.literal_eval(track_str)
            track = my_dict  # expect a dict with track info
            print(track)
        except Exception as e:
            print(e)
            print("hello")
            return JsonResponse({"status": "error", "message": "Invalid data"}, status=400)

        try:
            playlist = Playlist.objects.get(id=playlist_id)
        except (User.DoesNotExist, Playlist.DoesNotExist):
            return JsonResponse({"status": "error", "message": "Playlist not found"}, status=404)

        playlist.tracks.append(track)
        playlist.save()

        return JsonResponse({"status": "success", "playlist_name": playlist.title})
    print("hello1")
    return JsonResponse({"status": "error", "message": "Invalid request"}, status=400)



def setting_view(request):
    user_id = request.COOKIES.get("HIBIKI_USERNAME")
    user = None
    if user_id:
        user = get_object_or_404(User, username=user_id)
    
    context = {
        "user": user,  # pass the user object
    }
    return render(request, "setting.html", context)


def feedback_view(request):
    if request.method == "POST":
        form = FeedbackForm(request.POST)
        if form.is_valid():
            form.save()
            print("hello")
            return render(request, "setting.html")  # success page
    else:
        form = FeedbackForm()

    return render(request, "feedback_form.html", {"form": form})

def user_profile(request):
    user_id = request.COOKIES.get("HIBIKI_USERNAME")  # read cookie
    if not user_id:
        return render(request, "error.html", {"msg": "User not logged in"})

    user = get_object_or_404(User, username=user_id)
    return render(request, "user.html", {"user": user})


# About Us Page
def about_view(request):
    return render(request, "about.html")



def report_view(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        message = request.POST.get("message")
        url = request.POST.get("url", "")

        # Save in database
        Report.objects.create(
            name=name,
            email=email,
            message=message,
            url=url if url else None
        )

        messages.success(request, "✅ Thanks! Your report has been submitted.")
        return redirect("report")

    return render(request, "report.html")
def admin_dashboard(request):
    return render(request, "admin_dashboard.html")

def feedback_dashboard(request):
    feedbacks = Feedback.objects.all().order_by("-created_at")
    return render(request, "feedback_dashboard.html", {"feedbacks": feedbacks})

def reports_dashboard(request):
    reports = Report.objects.all().order_by("-created_at")
    return render(request, "reports_dashboard.html", {"reports": reports})


def logout_view(request):
    response = redirect("landing")
    response.delete_cookie("HIBIKI_USERNAME")
    return response

def format_seconds(seconds):
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    return f"{h}h {m}m {s}s"

def analytics_view(request):
    now = timezone.now()

    # --- Global song stats ---
    total_songs_played = SongPlay.objects.count()

    week_start = now - timedelta(days=7)
    songs_played_week = SongPlay.objects.filter(played_at__gte=week_start).count()

    month_start = now.replace(day=1)
    songs_played_month = SongPlay.objects.filter(played_at__gte=month_start).count()

    total_listening_time = SongPlay.objects.aggregate(total_time=Sum("duration"))["total_time"] or 0

    # --- Global user stats ---
    recent_active_users = User.objects.filter(
        last_login__gte=now - timedelta(days=1)
    ).count()
    total_users = User.objects.count()

    # Optionally, count guest plays (user=None)
    guest_plays = SongPlay.objects.filter(user__isnull=True).count()

    context = {
        "total_songs_played": total_songs_played,
        "songs_played_week": songs_played_week,
        "songs_played_month": songs_played_month,
        "total_listening_time": total_listening_time,
        "recent_active_users": recent_active_users,
        "total_users": total_users,
        "guest_plays": guest_plays,
        "total_listening_time_str": format_seconds(total_listening_time),
    }

    return render(request, "analytics.html", context)
