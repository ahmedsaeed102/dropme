from django.contrib import admin
from .models import Notification

@admin.register(Notification)
class MotificationAdmin(admin.ModelAdmin):
    list_display = ("user", "title_en", "is_read", "created_at")
    list_filter = ("user",)