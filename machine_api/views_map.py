from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point
from rest_framework.exceptions import NotFound
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from notification.services import notification_send_all
from .utlis import claculate_travel_distance_and_time, get_directions
from .serializers import MachineSerializer, MachineCoordinatesSerializer
from .models import Machine


class SetMachineCoordinates(APIView):
    """
    Assuming the machine has a GPS it should send a request to this endpoint to set its coordinates
        data schema: {
            longitude: float,
            latitdue: float
        }
    """

    permission_classes = [IsAuthenticated]
    serializer_class = MachineCoordinatesSerializer

    def patch(self, request, name):
        try:
            machine = Machine.objects.get(identification_name=name)
        except Machine.DoesNotExist:
            raise NotFound(detail="Error 404, Machine not found", code=404)

        longitude = request.data.get("longitude", 0)
        latitude = request.data.get("latitude", 0)

        if machine.location:
            notification_send_all(
                title="Machine location changed",
                body="A machine moved to a new location check it out!",
            )
        else:
            notification_send_all(
                title="Machine location changed",
                body="New recycle machine added check it out!",
            )

        pnt = Point(float(longitude), float(latitude))
        machine.location = pnt
        machine.save()

        serializer = MachineSerializer(machine)

        return Response(
            {
                "status": "success",
                "message": "set machine Coordinates successfully",
                "data": serializer.data,
            }
        )


class MachinesByCity(APIView):
    """
    Returns a all machines in given city
    """

    permission_classes = [IsAuthenticated]
    serializer_class = MachineSerializer

    def get(self, request, city):
        try:
            machines = Machine.objects.filter(city=city)
        except Machine.DoesNotExist:
            raise NotFound(detail="Error 404, Machine not found", code=404)

        serializer = MachineSerializer(machines, many=True)

        return Response(
            {
                "status": "success",
                "message": "got machines by city successfully",
                "data": serializer.data,
            }
        )


class GetNearestMachine(APIView):
    """
    Gives the nearest machine to the user
    Takes the long and lat of the user location
    Returns the machine information
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, long, lat):
        current_location = Point(float(long), float(lat), srid=4326)
        # machine = Machine.objects.filter(
        #     location__dwithin=(current_location, 0.45), # should convert km to degrees 1km = 1/111.325 degrees 0.45 = 50km
        #     status = 'available'
        #     ).annotate(
        #     distance=Distance('location', current_location, spheroid=True)).order_by('distance').first()
        machine = (
            Machine.objects.annotate(
                distance=Distance("location", current_location, spheroid=True)
            )
            .order_by("distance")
            .first()
        )
        if not machine:
            raise NotFound(
                detail="Error 404, there is no machine near the user", code=404
            )

        serializer = MachineSerializer(machine)
        # distance = geodesic(lonlat(*current_location.tuple), lonlat(*machine.location.tuple)).km

        return Response(
            {
                "status": "Success",
                "message": "got nearest machine successfully",
                "data": serializer.data,
            }
        )


class GetTravelInfo(APIView):
    """
    Takes the long and lat of the user location and the machine id
    Returns the machine information, the distance and the time it takes to go there
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, pk, long, lat):
        try:
            machine = Machine.objects.get(id=pk)
        except Machine.DoesNotExist:
            raise NotFound(detail="Error 404, Machine not found", code=404)

        current_location = Point(float(long), float(lat))

        serializer = MachineSerializer(machine)
        data = claculate_travel_distance_and_time(
            current_location.tuple, machine.location.tuple
        )

        return Response(
            {
                "status": "success",
                "message": "got travel info successfully",
                "data": {
                    "machine": serializer.data,
                    "distance meters": int(data["distance"]),
                    "timebyfoot minutes": int(data["timebyfoot"]),
                    "timebycar minutes": int(data["timebycar"]),
                    "timebybike minutes": int(data["timebybike"]),
                },
            }
        )


class GetDirections(APIView):
    """
    Get direction for a machine
    Takes the machine id and the user location
    Returns a path to the machine
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, pk, long, lat):
        try:
            machine = Machine.objects.get(id=pk)
        except Machine.DoesNotExist:
            raise NotFound(detail="Error 404, Machine not found", code=404)

        current_location = Point(float(long), float(lat))

        data = get_directions(current_location.tuple, machine.location.tuple)

        return Response(
            {
                "status": "success",
                "message": "got travel directions successfully",
                "data": data,
            }
        )
