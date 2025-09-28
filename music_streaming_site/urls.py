from django.contrib import admin
from django.urls import path, include
from hibiki import views

urlpatterns = [
    # path("__reload__/", include("django_browser_reload.urls")),
    path('admin/', admin.site.urls),
    path("", include("hibiki.urls")),
]
