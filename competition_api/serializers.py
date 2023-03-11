from rest_framework import serializers
from datetime import date
from users_api.models import UserModel
from .models import Competition, CompetitionRanking


class CompetitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Competition
        fields = '__all__'

    def validate(self, data):
        """
        validate Competition dates and target points
        """
        if data['start_date'] > data['end_date']:
            raise serializers.ValidationError("End date cannot be before start date")
        if data["start_date"] < date.today():
            raise serializers.ValidationError("Start date cannot be in the past")
        if data['target'] < 0:
            raise serializers.ValidationError("Target points can't be negative")
        
        return data

class CompetitionRankingSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompetitionRanking
        fields = '__all__'

class CustomUserSerializer(serializers.ModelSerializer):
    rank = serializers.ReadOnlyField(source='ranking')

    class Meta:
        model = UserModel
        fields = ['username', "total_points", 'rank']

