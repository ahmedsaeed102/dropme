from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Competition, CompetitionRanking, Resource

User = get_user_model()


class CompetitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Competition
        fields = "__all__"
        read_only_fields = ("created_at",)

    def validate(self, data):
        """
        validate Competition dates and target points
        """
        if data["start_date"] > data["end_date"]:
            raise serializers.ValidationError("End date cannot be before start date")

        if data["target"] < 0:
            raise serializers.ValidationError("Target points can't be negative")

        return data


class CompetitionRankingSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField(source="user.username")
    photo = serializers.SerializerMethodField()
    rank = serializers.ReadOnlyField(source="ranking")

    def get_photo(self, obj):
        photo = obj.user.profile_photo.url
        request = self.context.get("request")
        return request.build_absolute_uri(photo)

    class Meta:
        model = CompetitionRanking
        fields = ("name", "photo", "points", "rank")


class LeaderboardSerializer(serializers.ModelSerializer):
    rank = serializers.ReadOnlyField(source="ranking")

    class Meta:
        model = User
        fields = ["username", "profile_photo", "total_points", "rank"]


class ResourcesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resource
        fields = "__all__"


class ContactUsLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resource
        fields = ["name", "link"]
