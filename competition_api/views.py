from django.shortcuts import redirect
from rest_framework.exceptions import APIException, NotFound
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.views import APIView
from rest_framework.response import Response
from users_api.models import UserModel
from datetime import date
from .serializers import CompetitionSerializer, CustomUserSerializer, CustomCompetitionSerializer
from .models import Competition
from firebase_admin.messaging import Message, Notification
from fcm_django.models import FCMDevice


class Competitions(generics.ListCreateAPIView):
    # queryset = Competition.objects.all()
    queryset = Competition.objects.filter(end_date__gte=date.today()) # return only ongoing competitions
    serializer_class = CompetitionSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        # send notification to all user after a new competition is created
        serializer.save()
        FCMDevice.objects.send_message(
            Message(
            notification=Notification(
            title="New Competition", 
            body="New competition created check it out!", 
            )
            )
        )

    
class CompetitionDetail(generics.RetrieveUpdateAPIView):
    queryset = Competition.objects.all()
    serializer_class = CompetitionSerializer
    permission_classes = [IsAuthenticated]


class CompetitionDelete(generics.DestroyAPIView):
    queryset = Competition.objects.all()
    serializer_class = CompetitionSerializer
    permission_classes = [IsAdminUser]


# Global leaderboard
class Leaderboard(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        users = UserModel.objects.all()[:10]
        serializer = CustomUserSerializer(users, many=True, context={'request': request})
        current_user = {
            'username': request.user.username, 
            'photo': request.build_absolute_uri(request.user.profile_photo.url),
            'total_points': request.user.total_points,
            'rank': request.user.ranking
        }
        data={
            "status":'success',
            'message':'got leaderboard successfully',
            "data":{
                "current_user":current_user,
                "ranking": serializer.data
            }
        }
        
        return Response(data)


class JoinCompetition(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            competition = Competition.objects.get(pk=pk)
        except Competition.DoesNotExist:
            raise NotFound(detail="Error 404, competition not found", code=404)
        
        if competition.end_date < date.today():
            raise APIException(detail="Error 400, competition is over", code=400)
        
       
        if request.user in competition.users.all():
            raise APIException(detail="User Can't join same competition twice!", code=400)
        
        competition.users.add(request.user.pk)
        
        return redirect('competition_ranking', competition.pk)


class CompetitionRanking(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            competition = Competition.objects.get(pk=pk)
        except Competition.DoesNotExist:
            raise NotFound(detail="Error 404, competition not found", code=404)
        
        serializer = CustomCompetitionSerializer(competition, context={'request': request})

        currentuser = competition.users.filter(pk=request.user.pk).first()

        if currentuser:
            currentuser = competition.competitionranking_set.get(user=request.user.pk)
            current_user = {
                'username': request.user.username, 
                'photo':  request.build_absolute_uri(request.user.profile_photo.url),
                'points': currentuser.points,
                'rank' : currentuser.ranking
            }
        
        else:
            current_user = {
                'username': request.user.username, 
                'photo':  request.build_absolute_uri(request.user.profile_photo.url),
                'joined': False
            }
        
        data={
            "status":'success',
            'message':'got competition ranking successfully',
            "data":{
                "current_user":current_user,
                "ranking": serializer.data['top_ten']
            }
        }
        
        return Response(data)