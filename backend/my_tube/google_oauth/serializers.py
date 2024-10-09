from rest_framework import serializers
from .models import GoogleUser, User


class GoogleUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoogleUser
        fields = "__all__"


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"
