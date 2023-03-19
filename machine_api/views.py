import qrcode
from io import BytesIO
from django.core.files import File
from django.http import HttpResponse
from rest_framework import generics
from django.contrib.gis.geos import Point
from django.urls import reverse
from rest_framework.exceptions import NotFound
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.gis.db.models.functions import Distance
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Machine, RecycleLog
from .serializers import MachineSerializer, QRCodeSerializer, RecycleLogSerializer, CustomMachineSerializer
from .utlis import claculate_travel_distance_and_time, get_directions
# from geopy.distance import lonlat, geodesic


class Machines(generics.ListCreateAPIView):
    '''
    [GET] return all machines in database
    [Post] add new machine to database
    '''
    permission_classes = [IsAuthenticated]
    queryset = Machine.objects.all()
    serializer_class = MachineSerializer


class GetNearestMachine(APIView):
    '''
    Gives the nearest machine to the user
    Takes the long and lat of the user location
    Returns the machine information
    '''
    permission_classes = [IsAuthenticated]

    def get(self, request, long, lat):
        current_location = Point(float(long), float(lat))
        machine = Machine.objects.filter(
            location__dwithin=(current_location, 1000.0), # should convert km to degrees 1km = 1/111.325 degrees 0.45 = 50km
            status = 'available'
            ).annotate(
            distance=Distance('location', current_location, spheroid=True)).order_by('distance').first()
            
        if not machine:
            raise NotFound(detail="Error 404, there is no machine near the user", code=404)

        serializer = MachineSerializer(machine)
        # distance = geodesic(lonlat(*current_location.tuple), lonlat(*machine.location.tuple)).km
        
        return Response({
            'message': 'Success',
            'machine': serializer.data,
        })


class GetTravelInfo(APIView):
    '''
    Takes the long and lat of the user location and the machine id
    Returns the machine information, the distance and the time it takes to go there
    '''
    permission_classes = [IsAuthenticated]

    def get(self, request, pk, long, lat):
        try:
            machine = Machine.objects.get(id=pk)
        except Machine.DoesNotExist:
            raise NotFound(detail="Error 404, Machine not found", code=404)
        
        current_location = Point(float(long), float(lat))
        
        serializer = MachineSerializer(machine)
        data = claculate_travel_distance_and_time(current_location.tuple, machine.location.tuple)
        

        return Response({
            'message': 'Success',
            'machine': serializer.data,
            'distance meters': data['distance'],
            'timebyfoot minutes': data['timebyfoot'],
            'timebycar': data['timebycar'],
            'timebybike': data['timebybike'],
        })


class GetDirections(APIView):
    '''
    Get direction for a machine
    Takes the machine id and the user location
    Returns a path to the machine
    '''
    permission_classes = [IsAuthenticated]

    def get(self, request, pk, long, lat):
        try:
            machine = Machine.objects.get(id=pk)
        except Machine.DoesNotExist:
            raise NotFound(detail="Error 404, Machine not found", code=404)
        
        current_location = Point(float(long), float(lat))

        data = get_directions(current_location.tuple, machine.location.tuple)

        return Response({
            'message': 'Success',
            'directions': data,
        })


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
            longitude: float,
            latitdue: float
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
        
        pnt = Point(float(longitude), float(latitdue))
        machine.location = pnt
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