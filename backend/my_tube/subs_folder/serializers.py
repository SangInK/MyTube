from rest_framework import serializers
from .models import Folder, Subscription


class FolderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Folder
        fields = "__all__"


class SubscriptionSerializer(serializers.ModelSerializer):
    folder = FolderSerializer()

    class Meta:
        model = Subscription
        fields = "__all__"

    def create(self, validated_data):
        folder = validated_data.pop("folder")
        folder_queryset = Folder.objects.get(**folder)

        validated_data["folder"] = folder_queryset

        return Subscription.objects.create(**validated_data)
