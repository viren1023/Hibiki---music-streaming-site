import json
from ytmusicapi import YTMusic
from collections import defaultdict

ytmusic = YTMusic()

def home_metadata():
    home_recomendation = {}

    results = ytmusic.get_home()
    for res in results:
        home_recomendation[res["title"]] = res["contents"]
        
    with open("home_search_raw.json", "w", encoding="utf-8") as f:
        json.dump(home_recomendation, f, indent=2, ensure_ascii=False)
        
    return home_recomendation

def similar_search_metadata(query):
    similar_songs = defaultdict(list)
    results = ytmusic.search(query)

    for res in results[1:]:
        category_key = res["category"]

        # Add category field inside each item
        item_with_category = dict(res)
        item_with_category["category"] = res["category"]

        similar_songs[category_key].append(item_with_category)

    similar_songs = dict(similar_songs)
    
    with open("search.json", "w", encoding="utf-8") as f:
        json.dump(similar_songs, f, indent=2, ensure_ascii=False)

def similar_songs_name(query):
    results = []

    if len(query) >= 3:
        suggestions = ytmusic.get_search_suggestions(query)
        
        return suggestions
    
def playlist_metadata(playlistId):
    print("hi3")
    results = ytmusic.get_playlist(playlistId)
    print("hi4")
    with open("pl_search.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    return results

# def album_metadata(playlistId: str):
#     if not playlistId:
#         raise ValueError("Empty playlistId")

#     # Trim whitespace
#     playlistId = playlistId.strip()

#     # If '+' isn't present but there's a space, it likely came from URL-decoding.
#     # Restore pluses so we can split correctly.
#     if '+' not in playlistId and ' ' in playlistId:
#         playlistId = playlistId.replace(' ', '+')

#     # Only split once (in case ids themselves contain '+', unlikely)
#     parts = playlistId.split('+', 1)
#     playlist_id = parts[0]
#     album_id = parts[1] if len(parts) > 1 and parts[1] else None

#     # Fetch playlist
#     results_playlist = ytmusic.get_playlist(playlist_id)

#     # If we have an album_id, try to fetch and merge thumbnails
#     if album_id:
#         try:
#             results_album = ytmusic.get_album(album_id)
#             if results_album.get("thumbnails"):
#                 results_playlist["thumbnails"] = results_album["thumbnails"]
#                 results_playlist["description"] = results_album["description"]
#                 results_playlist["duration"] = results_album["duration"]
#         except Exception as e:
#             # decide how you want to handle fetch errors (log/ignore/raise)
#             print("Warning: album fetch failed:", e)

#     # Save for debugging if you want
#     with open("view_pl.json", "w", encoding="utf-8") as f:
#         json.dump(results_playlist, f, indent=2, ensure_ascii=False)

#     return results_playlist

def fetch_audio_metadata(videoId):
    results = ytmusic.get_song(videoId)
    videoDetails = results["videoDetails"]
    with open("search_raw.json", "w", encoding="utf-8") as f:
        json.dump(videoDetails, f, indent=2, ensure_ascii=False)
    audio_data = {
        "title": videoDetails.get("title"),
        "artists": [videoDetails.get("author")],
        "duration": videoDetails.get("lengthSeconds"),
        "thumbnail": videoDetails.get("thumbnail", {}).get("thumbnails", [{}])[-1].get("url", ""),
    }
    
    return audio_data

    