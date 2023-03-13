from rest_framework import serializers
from .models import Machine


class MachineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Machine
        fields = '__all__'
        read_only_fields = ('qr_code',)


class QRCodeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Machine
        fields = ['qr_code']