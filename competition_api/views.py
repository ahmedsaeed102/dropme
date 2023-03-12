from rest_framework.exceptions import APIException, NotFound
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from users_api.models import UserModel
from datetime import date
from .serializers import CompetitionSerializer, CustomUserSerializer
from .models import Competition, CompetitionRanking


class Competitions(generics.ListCreateAPIView):
    queryset = Competition.objects.all()
    serializer_class = CompetitionSerializer
    permission_classes = [IsAuthenticated]
    

class CompetitionDetail(generics.RetrieveUpdateAPIView):
    queryset = Competition.objects.all()
    serializer_class = CompetitionSerializer
    permission_classes = [IsAuthenticated]


class CompetitionDelete(generics.DestroyAPIView):
    queryset = Competition.objects.all()
    serializer_class = CompetitionSerializer
    permission_classes = [IsAuthenticated]

# Global leaderboard
class Leaderboard(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        users = UserModel.objects.all()[:10]
        serializer = CustomUserSerializer(users, many=True,)
        current_user = {
             'current_user': request.user.username, 
             'rank': request.user.ranking
        }
        data=[current_user]
        data.append(serializer.data)
        
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
        
        serializer = CompetitionSerializer(competition)

        return Response(serializer.data)


class CompetitionRanking(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        users = UserModel.objects.all()[:10]
        serializer = CustomUserSerializer(users, many=True,)
        current_user = {
             'current_user': request.user.username, 
             'rank': request.user.ranking
        }
        data=[current_user]
        data.append(serializer.data)
        
        return Response(data)
