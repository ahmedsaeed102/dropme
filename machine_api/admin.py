from django.contrib import admin
from .models import Machine
# Register your models here.

class MachineAdmin(admin.ModelAdmin):
    list_display = ['name', 'qr_code']
    readonly_fields = ['qr_code']

admin.site.register(Machine, MachineAdmin)