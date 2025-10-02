from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

# Create your models here.
class User(models.Model):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)

class Playlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="playlists")
    title = models.CharField(max_length=200)
    tracks = models.JSONField(default=list) 
    created_at = models.DateTimeField(auto_now_add=True)
    
class Feedback(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.rating}★)"


class Report(models.Model):
    name = models.CharField(max_length=150)
    email = models.EmailField()
    message = models.TextField()
    url = models.URLField(blank=True, null=True)  # optional
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Report by {self.name} ({self.email})"
    
class SongPlay(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="song_plays", null=True, blank=True)
    song_id = models.CharField(max_length=200)
    played_at = models.DateTimeField(auto_now_add=True)
    duration = models.PositiveIntegerField(help_text="Listened duration in seconds")
    
    def __str__(self):
        return f"{self.user.username if self.user else 'Guest'} played {self.song_id}"