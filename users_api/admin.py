from django.contrib import admin
from .models import UserModel, LocationModel


@admin.register(UserModel)
class Admin_dropMe(admin.ModelAdmin):
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
