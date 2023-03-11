from rest_framework import serializers
from datetime import date
from .models import Competition

class CompetitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Competition
        fields = '__all__'

    def validate(self, data):
        """
        validate Competition dates
        """
        if data['start_date'] > data['end_date']:
            raise serializers.ValidationError("End date cannot be before start date")
        elif data["start_date"] < date.today():
            raise serializers.ValidationError("Start date cannot be in the past")
        return data