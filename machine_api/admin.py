from django.contrib import admin
from .models import Machine, RecycleLog


class MachineAdmin(admin.ModelAdmin):
    list_display = ['identification_name', 'location', 'status']
    readonly_fields = ['qr_code']
    exclude=['longitude', 'latitdue']


class RecycleLogAdmin(admin.ModelAdmin):
    list_display = ['machine_name', 'bottles', 'cans', 'points', 'created_at']


admin.site.register(Machine, MachineAdmin)
admin.site.register(RecycleLog, RecycleLogAdmin)