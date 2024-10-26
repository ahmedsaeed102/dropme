import os
from django.db import models
from django.core.validators import FileExtensionValidator
from django.db.models.signals import post_save
from django.dispatch import receiver

from users_api.models import UserModel
from notification.services import notification_send_all

def messages_upload_to_imgs(instance, filename):
    return f"community/imgs/{instance.user_model.username}/{filename}"

def messages_upload_to_videos(instance, filename):
    return f"community/videos/{instance.user_model.username}/{filename}"

def messages_upload_to_files(instance, filename):
    return f"community/files/{instance.user_model.username}/{filename}"

def comments_upload_to_imgs(instance, filename):
    return f"community/comments/imgs/{instance.user_model.username}/{filename}"

def comments_upload_to_videos(instance, filename):
    return f"community/comments/videos/{instance.user_model.username}/{filename}"

def get_default():
    return {
        "Sad": {"count": 0, "users_ids": [], "users": []},
        "Wow": {"count": 0, "users_ids": [], "users": []},
        "Haha": {"count": 0, "users_ids": [], "users": []},
        "Like": {"count": 0, "users_ids": [], "users": []},
        "Love": {"count": 0, "users_ids": [], "users": []},
        "Angry": {"count": 0, "users_ids": [], "users": []},
    }

class CommentsModel(models.Model):
    user_model = models.ForeignKey(UserModel, related_name="comments", on_delete=models.CASCADE)
    content = models.CharField(max_length=4000, null=True, blank=True)
    comment_dt = models.DateTimeField(auto_now_add=True)
    reactions = models.JSONField(default=get_default)
    img = models.ImageField(upload_to=comments_upload_to_imgs, null=True, blank=True, validators=[FileExtensionValidator(allowed_extensions=["png", "jpeg", "jpg", "svg"])])
    video = models.FileField(upload_to=comments_upload_to_videos, null=True, blank=True, validators=[FileExtensionValidator(allowed_extensions=["MOV", "avi", "mp4", "webm", "mkv"])])

    class Meta:
        ordering = ("-comment_dt",)

    def __str__(self):
        return self.user_model.username

class MessagesModel(models.Model):
    user_model = models.ForeignKey(UserModel, related_name="messages", on_delete=models.CASCADE)
    content = models.CharField(max_length=4000, null=True, blank=True)
    message_dt = models.DateTimeField(auto_now_add=True)
    reactions = models.JSONField(default=get_default)
    comments = models.ManyToManyField(CommentsModel, blank=True, related_name="message_comment")
    img = models.ImageField(upload_to=messages_upload_to_imgs, null=True, blank=True, validators=[FileExtensionValidator(allowed_extensions=["png", "jpeg", "jpg", "svg"])])
    video = models.FileField(upload_to=messages_upload_to_videos, null=True, blank=True, validators=[FileExtensionValidator(allowed_extensions=["MOV", "avi", "mp4", "webm", "mkv"])])
    gif = models.ImageField(upload_to=messages_upload_to_imgs, null=True, blank=True, validators=[FileExtensionValidator(allowed_extensions=["gif"])])
    file = models.FileField(upload_to=messages_upload_to_files, null=True, blank=True)
    approved = models.BooleanField(default=False)

    class Meta:
        ordering = ("-message_dt",)

    def __str__(self):
        return self.user_model.username

    @property
    def comments_num(self):
        if self.comments:
            return self.comments.count()
        else:
            return 0

class ChannelsModel(models.Model):
    room_name = models.CharField(max_length=50)
    room_name_ar = models.CharField(max_length=50, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    description_ar = models.TextField(null=True, blank=True)
    channel_type = models.CharField(max_length=20, choices=[("public", "Public"), ("private", "Private")], default="public",)
    created_at = models.DateTimeField(auto_now_add=True)
    messages = models.ManyToManyField(MessagesModel, blank=True, related_name="message_channel")
    users = models.ManyToManyField(UserModel, related_name="user_channels", blank=True)
    is_admin_channel = models.BooleanField(default=False)
    notification_off_users = models.ManyToManyField(UserModel, related_name="notification_off_users", blank=True, null=True)

    @property
    def messages_num(self):
        return self.messages.filter(approved=True).count() if self.messages.exists() else 0

    @property
    def websocket_url(self):
        if not self.room_name:
            return ""
        if os.environ.get("state") == "production":
            return f"wss://dropme.up.railway.app/ws/chat/{self.room_name}/?token="
        else:
            return f"ws://localhost:8000/ws/chat/{self.room_name}/?token="

    def __str__(self):
        return self.room_name

@receiver(post_save, sender=ChannelsModel)
def channel_created(sender, instance, created, **kwargs):
    if created:
        notification_send_all(
            title="New community channel",
            body=f"""A new community channel '{instance.room_name}' has been created. Check it out!""",
            title_ar="قناة جديدة في المجتمع",
            body_ar=f"""لقد تم إنشاء قناة جديدة باسم '{instance.room_name_ar}'. انضم للمحادثة واستمتع بالتواصل!"""
        )

class ReportModel(models.Model):
    reporter = models.ForeignKey(UserModel, related_name="user_reports", on_delete=models.CASCADE)
    reported_message = models.ForeignKey(MessagesModel, related_name="message_reports", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.reporter.username + f" reported message: {self.reported_message.id}"

class Invitations(models.Model):
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name="user_invitations")
    invited = models.ForeignKey(UserModel, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"{self.user.username} -invited-> {self.invited.username}"
