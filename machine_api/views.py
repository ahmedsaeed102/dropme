from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Machine
from .serializers import MachineSerializer, QRCodeSerializer


class Machines(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Machine.objects.all()
    serializer_class = MachineSerializer
    

class MachineDetail(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Machine.objects.all()
    serializer_class = MachineSerializer


class MachineDelete(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Machine.objects.all()
    serializer_class = MachineSerializer
