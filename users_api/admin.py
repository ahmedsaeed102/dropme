from django.contrib import admin
from .models import UserModel, LocationModel, Feedback

@admin.register(UserModel)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ("id", "email", "username", "phone_number", "total_points", "address", "registered_at")
    search_fields = ("email", "phone_number", "username")
    list_filter = ("is_staff",)
    ordering = ("registered_at",)

admin.site.register(LocationModel)
admin.site.register(Feedback)
