from rest_framework import serializers
from .models import Machine, RecycleLog


class MachineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Machine
        exclude = ('qr_code', "longitude", 'latitdue')
        read_only_fields = ('location',)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        location = instance.location
        if location:
            location = [coord for coord in location]
            representation['location'] = {'longitude':location[0], 'latitude':location[1]}

        return representation


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


class UpdateRecycleLog(serializers.ModelSerializer):
    class Meta:
        model = RecycleLog
        fields = ['bottles', 'cans',]