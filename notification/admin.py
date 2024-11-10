from django.contrib import admin
from .models import Notification, NotificationImage

@admin.register(Notification)
class MotificationAdmin(admin.ModelAdmin):
    list_display = ("user", "title_en", "is_read", "created_at")
    list_filter = ("user",)

@admin.register(NotificationImage)
class NotificationImageAdmin(admin.ModelAdmin):
    list_display = ("name", "image")