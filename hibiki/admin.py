from django.contrib import admin
from .models import User,Playlist,Feedback,Report,SongPlay

admin.site.register(User)
admin.site.register(Playlist)
admin.site.register(Feedback)
admin.site.register(Report)
admin.site.register(SongPlay)