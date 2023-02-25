from django.contrib import admin
from django.contrib.gis import forms
from leaflet.forms.widgets import LeafletWidget
from django.contrib.gis.db import models
from .models import Machine

class MachineAdminForm(forms.ModelForm):
    class Meta:
        model = Machine
        fields = '__all__'
        widgets = {
            'location': LeafletWidget(),
        }
        formfield_overrides = {
            models.PointField: {'widget': LeafletWidget}
        }

class MachineAdmin(admin.ModelAdmin):
    form = MachineAdminForm

admin.site.register(Machine, MachineAdmin)