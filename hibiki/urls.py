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
    path("logout/", views.logout_view, name="logout"),
    
]
