from datetime import date
from django.shortcuts import redirect
from rest_framework.exceptions import ValidationError
from rest_framework import generics, serializers
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.views import APIView
from rest_framework.response import Response
from core.mixins import GetPermissionsMixin
from notification.services import notification_send_all
from users_api.models import UserModel
from .services import competition_get
from .serializers import (
    CompetitionSerializer,
    CustomCompetitionSerializer,
)
from .models import Competition, Resource


class Competitions(GetPermissionsMixin, generics.ListCreateAPIView):
    queryset = Competition.objects.filter(
        end_date__gte=date.today()
    )  # return only ongoing competitions
    serializer_class = CompetitionSerializer

    def perform_create(self, serializer):
        """send notification to all user after a new competition is created"""

        serializer.save()
        notification_send_all(
            title="New Competition", body="New competition created check it out!"
        )


class CompetitionDetail(GetPermissionsMixin, generics.RetrieveUpdateAPIView):
    queryset = Competition.objects.all()
    serializer_class = CompetitionSerializer
    http_method_names = ["head", "get", "put"]


class CompetitionDelete(generics.DestroyAPIView):
    queryset = Competition.objects.all()
    serializer_class = CompetitionSerializer
    permission_classes = [IsAdminUser]


class Leaderboard(APIView):
    """Global leaderboard"""

    permission_classes = [IsAuthenticated]

    class OutputSerializer(serializers.ModelSerializer):
        """custom serializer for global leaderboard"""

        rank = serializers.ReadOnlyField(source="ranking")

        class Meta:
            model = UserModel
            fields = ["username", "profile_photo", "total_points", "rank"]

    def get(self, request):
        users = UserModel.objects.all()[:10]
        serializer = self.OutputSerializer(
            users, many=True, context={"request": request}
        )
        current_user = {
            "username": request.user.username,
            "photo": request.build_absolute_uri(request.user.profile_photo.url),
            "total_points": request.user.total_points,
            "rank": request.user.ranking,
        }

        return Response(
            {
                "status": "success",
                "message": "got leaderboard successfully",
                "data": {"current_user": current_user, "ranking": serializer.data},
            }
        )


class JoinCompetition(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        competition = competition_get(pk=pk)

        if competition.end_date < date.today():
            raise ValidationError({"detail": "Error 400, competition is over"})

        if request.user in competition.users.all():
            return Response(
                {"detail": "You already joined this competition"}, status=400
            )

        competition.users.add(request.user.pk)

        return redirect("competition_ranking", competition.pk)


class CompetitionRanking(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        competition = competition_get(pk=pk)

        serializer = CustomCompetitionSerializer(
            competition, context={"request": request}
        )

        currentuser = competition.users.filter(pk=request.user.pk).first()

        if currentuser:
            currentuser = competition.competitionranking_set.get(user=request.user.pk)
            current_user = {
                "username": request.user.username,
                "photo": request.build_absolute_uri(request.user.profile_photo.url),
                "points": currentuser.points,
                "rank": currentuser.ranking,
            }

        else:
            current_user = {
                "username": request.user.username,
                "photo": request.build_absolute_uri(request.user.profile_photo.url),
                "joined": False,
            }

        return Response(
            {
                "status": "success",
                "message": "got competition ranking successfully",
                "data": {
                    "current_user": current_user,
                    "ranking": serializer.data["top_ten"],
                },
            }
        )


class AdsList(generics.ListAPIView):
    """For Home page slider"""

    class ResourcesSerializer(serializers.ModelSerializer):
        class Meta:
            model = Resource
            fields = "__all__"

    queryset = Resource.objects.filter(resource_type="ad")
    serializer_class = ResourcesSerializer
    permission_classes = [IsAuthenticated]
