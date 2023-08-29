from django.contrib import admin
from .models import UserModel, LocationModel, Feedback


@admin.register(UserModel)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "username",
        "email",
        "password",
        "profile_photo",
        "total_points",
        "address",
    )


admin.site.register(LocationModel)
admin.site.register(Feedback)
