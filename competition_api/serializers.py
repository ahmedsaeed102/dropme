from rest_framework import serializers
from users_api.models import UserModel
from .models import Competition, CompetitionRanking


class CompetitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Competition
        fields = '__all__'
        read_only_fields = ('created_at',)

    def validate(self, data):
        """
        validate Competition dates and target points
        """
        if data['start_date'] > data['end_date']:
            raise serializers.ValidationError("End date cannot be before start date")
        # if data["start_date"] < date.today():
            # raise serializers.ValidationError("Start date cannot be in the past")
        if data['target'] < 0:
            raise serializers.ValidationError("Target points can't be negative")
        
        return data


class CustomUserSerializer(serializers.ModelSerializer):
    rank = serializers.ReadOnlyField(source='ranking')

    class Meta:
        model = UserModel
        fields = ['username', 'profile_photo', "total_points", 'rank']


class CompetitionRankingSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField(source='user.username')
    # photo = serializers.ReadOnlyField(source='user.profile_photo.url')
    photo = serializers.SerializerMethodField()
    rank = serializers.ReadOnlyField(source='ranking')

    def get_photo(self,obj):
        photo = obj.profile_photo.url
        request = self.context.get("request")
        return request.build_absolute_uri(photo)
    
    class Meta:
        model = CompetitionRanking
        fields = ('name', 'photo', 'points', 'rank')


class CustomCompetitionSerializer(serializers.ModelSerializer):
    top_ten = serializers.SerializerMethodField()

    def get_top_ten(self, obj):
        ranking = obj.competitionranking_set.all()[:10] 
        return CompetitionRankingSerializer(ranking, many=True).data
    
    class Meta:
        model = Competition
        fields = ('top_ten',)


