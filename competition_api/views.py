from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from users_api.models import UserModel
from .serializers import CompetitionSerializer, CustomUserSerializer
from .models import Competition


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


#TODO: Join competition


#TODO: return competition leaderboard
    
