import qrcode
from io import BytesIO
from django.core.files import File
from django.http import HttpResponse
from rest_framework import generics
from django.urls import reverse
from rest_framework.exceptions import NotFound
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Machine, RecycleLog
from .serializers import MachineSerializer, QRCodeSerializer, RecycleLogSerializer, CustomMachineSerializer


class Machines(generics.ListCreateAPIView):
    '''
    [GET] return all machines in database
    [Post] add new machine to database
    '''
    permission_classes = [IsAuthenticated]
    queryset = Machine.objects.all()
    serializer_class = MachineSerializer


class MachinesByCity(APIView):
    '''
    Returns a all machines in given city
    '''
    permission_classes = [IsAuthenticated]
    serializer_class = MachineSerializer

    def get(self, request, city):
        try:
            machines = Machine.objects.filter(city=city)
        except Machine.DoesNotExist:
            raise NotFound(detail="Error 404, Machine not found", code=404)

        serializer = MachineSerializer(machines, many=True)

        return Response({
            'message': 'Success',
            'machines': serializer.data,
        })


class MachineDetail(generics.RetrieveUpdateAPIView):
    '''
    given an id return machine details
    '''
    permission_classes = [IsAuthenticated]
    queryset = Machine.objects.all()
    serializer_class = MachineSerializer


class SetMachineCoordinates(APIView):
    '''
    Assuming the machine has a GPS it should send a request to this endpoint to set its coordinates
        data schema: {
            longitude: decimal,
            latitdue: decimal
        } 
    '''
    permission_classes = [IsAuthenticated]
    serializer_class = CustomMachineSerializer

    def patch(self, request, name):
        try:
            machine = Machine.objects.get(identification_name=name)
        except Machine.DoesNotExist:
            raise NotFound(detail="Error 404, Machine not found", code=404)

        longitude = request.data.get('longitude', 0)
        latitdue = request.data.get('latitdue', 0)
        
        machine.longitude = longitude
        machine.latitdue = latitdue
        machine.save()

        serializer = MachineSerializer(machine)

        return Response({
            'message': 'Success',
            'machine': serializer.data,
        })



class MachineDelete(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Machine.objects.all()
    serializer_class = MachineSerializer


class MachineQRCode(APIView):
    '''
    Returns a QR code for the given machine name
    '''
    serializer_class = QRCodeSerializer

    def get(self, request, name):
        try:
            machine = Machine.objects.get(identification_name=name)
        except Machine.DoesNotExist:
            raise NotFound(detail="Error 404, Machine not found", code=404)

        # serializer = QRCodeSerializer(machine)
        path = request.build_absolute_uri(reverse("start_recycle", kwargs={'name':machine.identification_name}))
        qrcode_img = qrcode.make(path)
        fname = f'qr_code-{machine.identification_name}.png'
        buffer = BytesIO()
        qrcode_img.save(buffer,'PNG')
        machine.qr_code.save(fname, File(buffer), save=True)

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