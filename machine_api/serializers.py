from rest_framework import serializers
from .models import Machine, RecycleLog, MachineVideo
from .utlis import claculate_travel_distance

class MachineSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        current_location = self.context.get("current_location", None)
        representation = super().to_representation(instance)
        location = instance.location
        if location:
            if current_location:
                data = claculate_travel_distance(current_location.tuple, location.tuple)
                representation["distance"] = data
            location = [coord for coord in location]
            representation["location"] = {"longitude": location[0],"latitude": location[1],}
            representation["identification_name"] = instance.name_en
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

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["machine_name"] = instance.machine.name_en
        return representation

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

class MachineVideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = MachineVideo
        fields = ["video", "id"]