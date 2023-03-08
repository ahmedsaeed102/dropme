from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from .models import Machine
from .serializers import MachineSerializer


class ListMachines(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        machines = Machine.objects.all()
        serializer = MachineSerializer(machines, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class RetrieveMachine(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return Machine.objects.get(pk=pk)
        except Machine.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        machine = self.get_object(pk)
        serializer = MachineSerializer(machine)
        return Response(serializer.data, status=status.HTTP_200_OK)
