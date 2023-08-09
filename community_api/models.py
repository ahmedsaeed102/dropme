import os
from django.db import models
from django.core.validators import FileExtensionValidator
from users_api.models import UserModel


def upload_to_imgs(instance, filename):
    return f"community/imgs/{instance.user_model.username}/{filename}"


def upload_to_videos(instance, filename):
    return f"community/videos/{instance.user_model.username}/{filename}"


class MessagesModel(models.Model):
    user_model = models.ForeignKey(
        UserModel, related_name="messages", on_delete=models.CASCADE
    )
    content = models.CharField(max_length=4000, null=True, blank=True)
    message_dt = models.DateTimeField(auto_now_add=True)

    reactions = models.JSONField(default=dict)

    img = models.ImageField(
        upload_to=upload_to_imgs,
        null=True,
        blank=True,
        validators=[
            FileExtensionValidator(allowed_extensions=["png", "jpeg", "jpg", "svg"]),
        ],
    )
    video = models.FileField(
        upload_to=upload_to_videos,
        null=True,
        blank=True,
        validators=[
            FileExtensionValidator(
                allowed_extensions=["MOV", "avi", "mp4", "webm", "mkv"]
            )
        ],
    )

    class Meta:
        ordering = ("-message_dt",)

    def __str__(self):
        return self.user_model.username


class ChannelsModel(models.Model):
    room_name = models.CharField(max_length=50)
    room_name_ar = models.CharField(max_length=50, null=True, blank=True)

    description = models.TextField(null=True, blank=True)
    description_ar = models.TextField(null=True, blank=True)

    channel_type = models.CharField(
        max_length=20,
        choices=[("public", "Public"), ("private", "Private")],
        default="public",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    messages = models.ManyToManyField(MessagesModel, blank=True)
    users = models.ManyToManyField(UserModel, related_name="user_channels", blank=True)

    @property
    def messages_num(self):
        """return the number of messages inside specific channel"""
        if self.messages and self.room_name:
            return self.messages.count()
        else:
            return 0

    @property
    def websocket_url(self):
        """return the websocket url of specific channel"""
        if self.room_name:
            if os.environ.get("state") == "production":
                return f"wss://dropme.up.railway.app/ws/chat/{self.room_name}/?token="
            else:
                return f"ws://localhost:8000/ws/chat/{self.room_name}/?token="
        else:
            return ""

    def __str__(self):
        return self.room_name


class ReportModel(models.Model):
    reporter = models.ForeignKey(
        UserModel, related_name="user_reports", on_delete=models.CASCADE
    )
    reported_message = models.ForeignKey(
        MessagesModel, related_name="message_reports", on_delete=models.CASCADE
    )

    created_at = models.DateTimeField(auto_now_add=True)
