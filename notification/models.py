from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Notification(models.Model):
    title = models.CharField(max_length=100)
    body = models.TextField()

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="notifications"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username
