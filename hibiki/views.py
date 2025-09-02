import random
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .models import User
from django.http import HttpResponse
from .forms import RegisterForm, LoginForm
from datetime import date


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

def home(request):
    username = request.COOKIES.get('HIBIKI_USERNAME', 'default username')
    context = {
        "username": username,
        "playlists": [
            {"title": "Study Beats", "tag": "Chill","img":"https://picsum.photos/400/250?random="+f"{random.randint(1,1000)}"},
            {"title": "Rainy Morning", "tag": "Jazzy","img":"https://picsum.photos/400/250?random="+f"{random.randint(1,1000)}"},
            {"title": "Skate Punk", "tag": "Weekend","img":"https://picsum.photos/400/250?random="+f"{random.randint(1,1000)}"},
            {"title": "Folk Music", "tag": "Traditional","img":"https://picsum.photos/400/250?random="+f"{random.randint(1,1000)}"},
        ],
        "recommendations": [
            {"title": "Artists", "tag": "Your Top","img":"https://picsum.photos/400/250?random="+f"{random.randint(1,1000)}"},
            {"title": "Pop Music", "tag": "Best Of","img":"https://picsum.photos/400/250?random="+f"{random.randint(1,1000)}"},
            {"title": "2022", "tag": "Your Year","img":"https://picsum.photos/400/250?random="+f"{random.randint(1,1000)}"},
        ],
        "popular_songs": [
            {"title": "Call Living", "artist": "Tom","img":"https://picsum.photos/400/250?random="+f"{random.randint(1,1000)}"},
            {"title": "On The Top", "artist": "Alma","img":"https://picsum.photos/400/250?random="+f"{random.randint(1,1000)}"},
            {"title": "Together", "artist": "Jonas&Jonas","img":"https://picsum.photos/400/250?random="+f"{random.randint(1,1000)}"},
        ],
    }
    return render(request, "home.html", context)

def logout_view(request):
    response = redirect("landing")
    response.delete_cookie("HIBIKI_USERNAME")
    return response