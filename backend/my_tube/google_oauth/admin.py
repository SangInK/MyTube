from django.contrib import admin
from .models import GoogleUser, User

admin.site.register(GoogleUser)
admin.site.register(User)
