from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
from .serializers import CompetitionSerializer
from .models import Competition


class Competitions(generics.ListCreateAPIView):
    queryset = Competition.objects.all()
    serializer_class = CompetitionSerializer
    permission_classes = [IsAuthenticated]
    
    # def get_queryset(self):
    #     return self.queryset.filter(user=self.request.user)

    # def perform_create(self, serializer):
    #     serializer.save(user=self.request.user)
