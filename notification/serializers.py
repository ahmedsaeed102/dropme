from rest_framework.serializers import ModelSerializer
from .models import Notification
from rest_framework import serializers

class NotificationSerializer(ModelSerializer):
    class Meta:
        model = Notification
        fields = "__all__"

class NotificationUpdateSerializer(ModelSerializer):
    all_notifications = serializers.BooleanField(required=False)
    list_notifications = serializers.ListField(child=serializers.IntegerField(), required=False)