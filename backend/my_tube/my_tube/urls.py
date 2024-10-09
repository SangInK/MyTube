from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("auth/", include("google_oauth.urls")),
    path("subs/", include("subs_folder.urls")),
]
