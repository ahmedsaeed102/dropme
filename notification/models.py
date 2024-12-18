from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

def user_notifications_imgs(instance, filename):
    return f"notifications/{instance.user.username}/{filename}"

def notification_imgs(instance, filename):
    return f"notifications/{filename}"

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    title_ar = models.CharField(max_length=100, null=True, blank=True)
    title_en = models.CharField(max_length=100, null=True, blank=True)
    body_ar = models.TextField(null=True, blank=True)
    body_en = models.TextField(null=True, blank=True)
    type = models.CharField(max_length=100, null=True, blank=True)
    extra_data = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    image = models.ImageField(upload_to=user_notifications_imgs, null=True, blank=True)

    def __str__(self):
        return self.user.username

class NotificationImage(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    image = models.ImageField(upload_to=notification_imgs, null=True, blank=True)

    def __str__(self):
        return self.name