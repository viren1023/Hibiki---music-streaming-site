from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

# Create your models here.
class User(models.Model):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    
class Playlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="playlists")
    name = models.CharField(max_length=200)
    total_songs = models.PositiveIntegerField(default=0)   # ✅ store song count
    created_at = models.DateTimeField(auto_now_add=True)
    
class PlaylistSong(models.Model):
    playlist = models.ForeignKey(
        Playlist, on_delete=models.CASCADE, related_name="songs"
    )
    song_id = models.CharField(max_length=200)   # or IntegerField if numeric IDs
    order = models.PositiveIntegerField(default=0)

@receiver([post_save, post_delete], sender=PlaylistSong)
def update_total_songs(sender, instance, **kwargs):
    playlist = instance.playlist
    playlist.total_songs = playlist.songs.count()
    playlist.save(update_fields=["total_songs"])