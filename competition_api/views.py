from datetime import date
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from rest_framework import generics
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from core.mixins import AdminOrReadOnlyPermissionMixin

from notification.services import notification_send_all
from .services import competition_get, current_user_ranking, competition_ranking
from .serializers import CompetitionSerializer, LeaderboardSerializer, ResourcesSerializer, ContactUsLinkSerializer
from .models import Competition, Resource

User = get_user_model()

class Leaderboard(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = LeaderboardSerializer

    def get(self, request):
        top_ten = User.objects.all()[:10]
        serializer = self.serializer_class(top_ten, many=True, context={"request": request})
        current_user = current_user_ranking(request=request)
        return Response(
            {
                "status": "success",
                "message": "got leaderboard successfully",
                "data": {"current_user": current_user, "ranking": serializer.data},
            }
        )

class Competitions(AdminOrReadOnlyPermissionMixin, generics.ListCreateAPIView):
    queryset = Competition.objects.filter(end_date__gte=date.today())
    serializer_class = CompetitionSerializer

    def perform_create(self, serializer):
        serializer.save()

    @method_decorator(cache_page(60 * 30))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

class CompetitionDetail(AdminOrReadOnlyPermissionMixin, generics.RetrieveUpdateAPIView):
    queryset = Competition.objects.all()
    serializer_class = CompetitionSerializer
    http_method_names = ["head", "get", "put"]

class CompetitionDelete(AdminOrReadOnlyPermissionMixin, generics.DestroyAPIView):
    queryset = Competition.objects.all()
    serializer_class = CompetitionSerializer

class JoinCompetition(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        competition = competition_get(pk=pk)
        if competition.end_date < date.today():
            raise ValidationError({"detail": _("Competition has already ended")})
        if request.user in competition.users.all():
            raise ValidationError({"detail": _("You already joined this competition")})
        competition.users.add(request.user.pk)
        return redirect("competition_ranking", competition.pk)

class leaveCompetition(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        competition = competition_get(pk=pk)
        if competition.end_date < date.today():
            raise ValidationError({"detail": _("Competition has already ended")})
        if not request.user in competition.users.all():
            raise ValidationError({"detail": _("You already not joined this competition")})
        competition.users.remove(request.user.pk)
        return Response("Left competition successfully", status = 200)

class CompetitionRanking(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        competition = competition_get(pk=pk)
        ranking = competition_ranking(request=request, competition=competition)
        return Response(ranking)

class LinksAPI(generics.ListAPIView):
    queryset = Resource.objects.filter(resource_type="contact_us")
    serializer_class = ContactUsLinkSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        data = super().get(request, *args, **kwargs).data
        new_data = {}
        for item in data:
            new_data[item["name"]] = item["link"]
        return Response(new_data)
