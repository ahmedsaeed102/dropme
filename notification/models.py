from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    title_ar = models.CharField(max_length=100, null=True, blank=True)
    title_en = models.CharField(max_length=100, null=True, blank=True)
    body_ar = models.TextField(null=True, blank=True)
    body_en = models.TextField(null=True, blank=True)
    navigation = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username
