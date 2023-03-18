from rest_framework import serializers
from .models import Machine, RecycleLog


class MachineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Machine
        # fields = '__all__'
        exclude = ('qr_code', )
        # read_only_fields = ('qr_code',)


class CustomMachineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Machine
        fields = ['longitude', 'latitdue']


class QRCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Machine
        fields = ['qr_code']


class RecycleLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecycleLog
        fields = ['machine_name', 'bottles', 'cans', 'created_at']