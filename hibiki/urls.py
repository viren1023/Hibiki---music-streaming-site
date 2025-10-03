from django.urls import path
from . import views
from django.views.generic import RedirectView
from django.conf import settings
from django.urls import path

urlpatterns = [
    path('logo.png', RedirectView.as_view(url=settings.STATIC_URL + 'hibiki/logo.png')),
    path('favicon.ico', RedirectView.as_view(url=settings.STATIC_URL + 'hibiki/favicon.ico')),
    path("", views.landing_view, name="landing"),
    path("login/", views.login_view, name="login"),
    path("register/", views.register_view, name="register"),
    path("home/", views.home, name="home"),
    path("search/", views.search_page, name="search"),
    path("similar_songs/", views.similar_name, name="similar_name"),
    path("playlist/", views.playlist_view, name="playlist"),
    # path("player", views.player_view, name="player"),
    # path('player/song/', views.player_view, name='player_song'),
    path('get_audio_url', views.get_audio_url, name='get_audio_url'),
    path("moods/", views.moods_view, name="moods"),
    path("api/player/", views.player_api, name="player_api"),
    path("my-playlist/", views.user_playlist, name="myPlaylist"),
    path("my-playlists/create/", views.create_playlist, name="create_playlist"),
    path("my-playlists/<int:pk>/delete/", views.delete_playlist, name="delete_playlist"),
    path("precache_audio_urls/", views.precache_audio_urls, name="cache-next-songs"),
    path('show-playlist/', views.show_playlist, name='show_playlist'),
    path('add_to_playlist/', views.add_to_playlist, name='add_to_playlist'),
    path("setting/", views.setting_view, name="setting"),
    path("feedback/", views.feedback_view, name="feedback"),
    path("feedback-dashboard/", views.feedback_dashboard, name="feedback_dashboard"),
    path("report/", views.report_view, name="report"),
    path("admin-dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path("reports-dashboard/", views.reports_dashboard, name="reports_dashboard"),
    path("analytics-dashboard/", views.analytics_view, name="analytics_dashboard"),
    path("about/", views.about_view, name="about"),
    path("logout/", views.logout_view, name="logout"),
]
