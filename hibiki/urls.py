from django.urls import path
from . import views

urlpatterns = [
    path("", views.landing_view, name="landing"),
    path("login/", views.login_view, name="login"),
    path("register/", views.register_view, name="register"),
    path("home/", views.home, name="home"),
    path("search/", views.search_page, name="search"),
    path("similar_songs/", views.similar_name, name="similar_name"),
    path("playlist/", views.playlist_view, name="playlist"),
    # path("player", views.player_view, name="player"),
    # path('player/song/', views.player_view, name='player_song'),
    path("logout/", views.logout_view, name="logout"),
    path('get_audio_url', views.get_audio_url, name='get_audio_url'),
    path("moods/", views.moods_view, name="moods"),
    path("my-playlist/", views.user_playlist, name="myPlaylist"),
    path("api/player/", views.player_api, name="player_api"),
]
