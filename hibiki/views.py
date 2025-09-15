import random
from ytmusicapi import YTMusic
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .models import User
import yt_dlp
from django.http import HttpResponse, JsonResponse
from .forms import RegisterForm, LoginForm
from datetime import date
from .core_logic.fetchmetadata import home_metadata, similar_search_metadata, similar_songs_name, playlist_metadata, fetch_audio_metadata
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

            try:
                user = User.objects.get(username=username, password=password)
            except User.DoesNotExist:
                messages.error(request, "Invalid username or password")
                return redirect("login")

            response = redirect("home")
            response.set_cookie(
                key="HIBIKI_USERNAME",
                value=user.username,
                max_age=3600,  # 1 hour
                httponly=True,
                secure=False,  # set True if HTTPS
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
            response = redirect("home")
            response.set_cookie(
                key="HIBIKI_USERNAME",
                value=user.username,
                max_age=3600,
                httponly=True,
                secure=False,   # set True if using HTTPS
            )
            return response
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = RegisterForm()

    return render(request, "register.html", {"form": form})

# def home(request):
#     similar_search_metadata()
#     result = home_metadata()
#     username = request.COOKIES.get('HIBIKI_USERNAME', 'default username')
#     context = {
#         "username": username,
#         "playlists": [
#             {"title": "Study Beats", "tag": "Chill","img":"https://picsum.photos/400/250?random="+f"{random.randint(1,1000)}"},
#             {"title": "Rainy Morning", "tag": "Jazzy","img":"https://picsum.photos/400/250?random="+f"{random.randint(1,1000)}"},
#             {"title": "Skate Punk", "tag": "Weekend","img":"https://picsum.photos/400/250?random="+f"{random.randint(1,1000)}"},
#             {"title": "Folk Music", "tag": "Traditional","img":"https://picsum.photos/400/250?random="+f"{random.randint(1,1000)}"},
#         ],
#         "recommendations": [
#             {"title": "Artists", "tag": "Your Top","img":"https://picsum.photos/400/250?random="+f"{random.randint(1,1000)}"},
#             {"title": "Pop Music", "tag": "Best Of","img":"https://picsum.photos/400/250?random="+f"{random.randint(1,1000)}"},
#             {"title": "2022", "tag": "Your Year","img":"https://picsum.photos/400/250?random="+f"{random.randint(1,1000)}"},
#         ],
#         "popular_songs": [
#             {"title": "Call Living", "artist": "Tom","img":"https://picsum.photos/400/250?random="+f"{random.randint(1,1000)}"},
#             {"title": "On The Top", "artist": "Alma","img":"https://picsum.photos/400/250?random="+f"{random.randint(1,1000)}"},
#             {"title": "Together", "artist": "Jonas&Jonas","img":"https://picsum.photos/400/250?random="+f"{random.randint(1,1000)}"},
#         ],
#     }
#     return render(request, "home.html", context)

def home(request):
    # fetch data from YTMusic
    result = home_metadata()
    result_key=list(result.keys())
    username = request.COOKIES.get('HIBIKI_USERNAME', 'default username')
    
    get_item_type = lambda item: (
        "song" if item.get("videoId") 
        else "playlist" if item.get("playlistId")
        else "album" if item.get("audioPlaylistId") 
        else None
    )


    # playlists -> from "Trending community playlists"
    section1 = []
    for item in result.get(f"{result_key[1]}", [])[:4]:
        section1.append({
            "title": item.get("title"),
            "tag": item.get("description", ""),
            "id": item.get("videoId") or item.get("playlistId") or item.get("audioPlaylistId"),
            "type" : get_item_type,
            "img": item["thumbnails"][0]["url"] if item.get("thumbnails") else "https://picsum.photos/400/250?random="+f"{random.randint(1,1000)}"
        })

    # recommendations -> from "Albums for you"
    section2 = []
    for item in result.get(f"{result_key[2]}", [])[:3]:
        section2.append({
            "title": item.get("title"),
            "tag": item.get("type", "Album"),
            "id": item.get("videoId") or item.get("playlistId") or item.get("audioPlaylistId"),
            "type" : get_item_type,
            "img": item["thumbnails"][0]["url"] if item.get("thumbnails") else "https://picsum.photos/400/250?random="+f"{random.randint(1,1000)}"
        })

    # popular songs -> from "Quick picks"
    section3 = []
    for item in result.get(f"{result_key[0]}", [])[:12]:
        section3.append({
            "title": item.get("title"),
            "artist": ", ".join([artist["name"] for artist in item.get("artists", [])]),
            "id": item.get("videoId") or item.get("playlistId") or item.get("audioPlaylistId"),
            "type" : get_item_type,
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

ytmusic = YTMusic()

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
            results = ytmusic.search(query)
            search_results = results[:10]
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
        charts = ytmusic.get_charts(country="IN")  # You can change country
        return render(request, "search.html", {
            "query": query,
            "results": search_results,
            "mood_categories": mood_categories["Moods & moments"] ,
            "charts": charts["weekly"] 
        })
    


# def fetch_audio(request):
#     name = request.GET.get("name")
#     if not name:
#         return JsonResponse({"error": "No song name provided"}, status=400)
#     pass

def playlist_view(request):
    playlistId = request.GET.get("id", "")
    playlist = playlist_metadata(playlistId)
        
    context = {
        "playlist": playlist,
        "tracks": playlist["tracks"],
    }
    return render(request, "playlist.html", context)

# def get_playlist_audio_urls():
# def get_playlist_audio_urls(request):
#     # Example: List of tracks
#     playlist = [
#         {"video_id": "cvQWzlNIjt8", "title": "Song 1", "artists": ["Artist A"], "thumbnail": "https://example.com/thumb1.jpg"},
#         {"video_id": "kUYzsGZ6yQ8", "title": "Song 2", "artists": ["Artist B"], "thumbnail": "https://example.com/thumb2.jpg"},
#         # Add more tracks...
#     ]

#     current_index = int(request.GET.get("index", 0))  # Start from index 0 by default
#     current_track = playlist[current_index]

#     return render(request, "player.html", {
#         "playlist": playlist,
#         "current_index": current_index,
#         "current_track": current_track,
#     })

def player_view(request):
    print("hi1")
    video_id = request.GET.get("songId")
    playlist_id = request.GET.get("playlistId")
    if (video_id):
        audio_data = fetch_audio_metadata(video_id)
        return render(request, "player.html", {
            "type": "song",
            "video_id": video_id,
            "audio_data": audio_data
        })
    
    elif(playlist_id):
        print("hi2")
        playlist_id = request.GET.get("playlistId")
        print(playlist_id)
        playlist = playlist_metadata(playlist_id)
        print("hi5")
        tracks = playlist.get("tracks", [])
        print("hi6")
        # filtered_tracks = [
        # {
        #     "videoId": track.get("videoId"),
        #     "title": track.get("title"),
        #     "artists": track.get("artists"),
        #     "thumbnails": track.get("thumbnails"),
        #     "duration": track.get("duration"),
        # } for track in tracks
        # ]
        # Pass playlist and current index to player
        return render(request, "player.html", {
            "type": "playlist",
            "playlist": tracks,
            "current_index": 0,
        })

def get_audio_url(request):
    video_id = request.GET.get("video_id")
    if not video_id:
        return JsonResponse({"error": "No video_id provided"}, status=400)

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
                return JsonResponse({"audio_url": audio_url})
            else:
                return JsonResponse({"error": "Failed to extract audio URL"}, status=500)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

def logout_view(request):
    response = redirect("landing")
    response.delete_cookie("HIBIKI_USERNAME")
    return response

