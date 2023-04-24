from django.contrib import admin
from .import models 

@admin.register(models.UserModel)
class Admin_dropMe(admin.ModelAdmin):
    list_display=('id','username','email','password','profile_photo','total_points','address')
            
admin.site.register(models.LocationModel)