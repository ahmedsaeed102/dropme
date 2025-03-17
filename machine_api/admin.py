from django.contrib import admin
from .models import Machine, RecycleLog, PhoneNumber, MachineVideo

class MachineAdmin(admin.ModelAdmin):
    list_display = ["identification_name", "location", "status"]
    readonly_fields = ["qr_code"]
    exclude = ["longitude", "latitdue"]

class RecycleLogAdmin(admin.ModelAdmin):
    list_display = ["user", "phone", "machine", "bottles", "cans", "points", "in_progess", "is_complete", "created_at"]
    search_fields = ("user", "phone")

class MachineVideoAdmin(admin.ModelAdmin):
    list_display = ["id", "video"]

class PhoneNumberAdmin(admin.ModelAdmin):
    list_display = ["phone_number", "points"]
    search_fields = ("phone_number", )

admin.site.register(Machine, MachineAdmin)
admin.site.register(RecycleLog, RecycleLogAdmin)
admin.site.register(PhoneNumber, PhoneNumberAdmin)
admin.site.register(MachineVideo, MachineVideoAdmin)
