from rest_framework import serializers
from .models import Machine, RecycleLog

class MachineSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        location = instance.location
        if location:
            location = [coord for coord in location]
            representation["location"] = {"longitude": location[0],"latitude": location[1],}
        return representation

    class Meta:
        model = Machine
        exclude = ("qr_code",)
        read_only_fields = ("location",)

class FilterSerializer(serializers.Serializer):
        identification_name = serializers.CharField(required=False)
        city = serializers.CharField(required=False)
        place = serializers.CharField(required=False)

class RecycleLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecycleLog
        fields = ["machine_name", "bottles", "cans", "points", "created_at"]

class MachineCoordinatesSerializer(serializers.Serializer):
    longitude = serializers.FloatField()
    latitude = serializers.FloatField()

class QRCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Machine
        fields = ["qr_code"]

class UpdateRecycleLog(serializers.ModelSerializer):
    class Meta:
        model = RecycleLog
        fields = ["bottles", "cans"]