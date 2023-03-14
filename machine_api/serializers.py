from rest_framework import serializers
from .models import Machine, RecycleLog


class MachineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Machine
        fields = '__all__'
        read_only_fields = ('qr_code',)


class QRCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Machine
        fields = ['qr_code']


class RecycleLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecycleLog
        fields = ['machine_name', 'bottles', 'cans', 'created_at']