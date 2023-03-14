from django.http import HttpResponse
from rest_framework import generics
from rest_framework.exceptions import NotFound
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
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
    serializer_class = QRCodeSerializer

    def get(self, request, name):
        try:
            machine = Machine.objects.get(identification_name=name)
        except Machine.DoesNotExist:
            raise NotFound(detail="Error 404, Machine not found", code=404)

        # serializer = QRCodeSerializer(machine)

        # return Response({
        #     'message': 'Success',
        #     'machine pk': machine.pk,
        #     'qr_code': serializer.data})
        return HttpResponse(machine.qr_code, content_type="image/png")


class UpdateRecycle(APIView):
    '''
    The machine should send a request to this endpoint with the number of items recycled
    data schema: {
    bottles: int,
    cans: int
    } 
    '''
    # permission_classes = [IsAuthenticated] removed for now
    def post(self, request, name):
        bottles = request.data.get('bottles', 0)
        cans = request.data.get('cans', 0)
        log = RecycleLog.objects.filter(machine_name=name, in_progess=True).first()

        if not log:
            raise NotFound(detail="Error 404, log not found", code=404)
        
        points = (bottles + cans) * 10

        log.bottles = bottles
        log.cans = cans
        log.points = points
        log.in_progess = False
        log.is_complete= True
        log.save()
        channel_layer = get_channel_layer()
        try:
            async_to_sync(channel_layer.send)(log.channel_name,{
                "type": "receive.update",
                'bottles':log.bottles,
                'cans': log.cans,
                'points': log.points
            })
        except Exception as e:
            print(e)
            return Response({'message':'failed!'})


        return Response({"message":"success", 'bottles':bottles, 'cans': cans})
    

class RetrieveRecycleLog(APIView):
    '''
    Retrieve the user's recycling logs
    '''
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