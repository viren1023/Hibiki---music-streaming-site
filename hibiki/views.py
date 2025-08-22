from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .models import User

def landing_view(request):
    return render(request, "landing.html")

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        print(username, password)
        
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            messages.error(request, "Invalid username or password")
            return redirect("login")

        # Compare raw password with hashed one
        try:
            password = User.objects.get(password=password)
        except User.DoesNotExist:
            messages.error(request, "Invalid username or password")
            return redirect("login")
        return redirect("home")  # Homepage after successful login
        
    return render(request, "login.html")

def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
        email = request.POST.get("email")

        if password != confirm_password:
            messages.error(request, "Passwords do not match")
            return redirect("register")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken")
            return redirect("register")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered")
            return redirect("register")

        user = User.objects.create(username=username, password=password, email=email)
        user.save()
        # login(request, user)  # Auto-login after registration
        return redirect("home")  # Homepage

    return render(request, "register.html")

def home(request):
    context = {
        "username": "username",
        "playlists": [
            {"title": "Study Beats", "tag": "Chill"},
            {"title": "Rainy Morning", "tag": "Jazzy"},
            {"title": "Skate Punk", "tag": "Weekend"},
            {"title": "Folk Music", "tag": "Traditional"},
        ],
        "recommendations": [
            {"title": "Artists", "tag": "Your Top"},
            {"title": "Pop Music", "tag": "Best Of"},
            {"title": "2022", "tag": "Your Year"},
        ],
        "popular_songs": [
            {"title": "Call Living", "artist": "Tom", "image": "tom.jpg"},
            {"title": "On The Top", "artist": "Alma", "image": "alma.jpg"},
            {"title": "Together", "artist": "Jonas&Jonas", "image": "jonas.jpg"},
        ],
    }
    return render(request, "home.html", context)