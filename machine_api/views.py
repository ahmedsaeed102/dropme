from rest_framework import generics
from rest_framework.exceptions import NotFound
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Machine, RecycleLog
from .serializers import MachineSerializer, QRCodeSerializer, RecycleLogSerializer


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


class MachineQRCode(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = QRCodeSerializer

    def get(self, request, name):
        try:
            machine = Machine.objects.get(identification_name=name)
        except Machine.DoesNotExist:
            raise NotFound(detail="Error 404, Machine not found", code=404)

        serializer = QRCodeSerializer(machine)

        return Response({
            'message': 'Success',
            'machine pk': machine.pk,
            'qr_code': serializer.data})

# this class should open a socket connection between server and mobile app until recycling is done
# it should also claculate the points and add it to user total points, and if
# there is a ongoing competion, it should add it to user competition points
class StartRecycle(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, name):
        return Response({"message":"success", 'id':name})
    

class RetrieveRecycleLog(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = RecycleLogSerializer

    def get(self, request, pk):
        logs = RecycleLog.objects.filter(user=pk, is_complete=True)
        if not logs:
            raise NotFound(detail="Error 404, no logs for current user", code=404)

        serializer = RecycleLogSerializer(logs, many=True)

        return Response({
            'message': 'Success',
            'data': serializer.data,})