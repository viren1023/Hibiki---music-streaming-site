from django.contrib import admin
from .models import User
from .models import Playlist

admin.site.register(User)
admin.site.register(Playlist)