from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import generics, serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from drf_spectacular.utils import extend_schema, OpenApiParameter
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point
from .utlis import claculate_travel_distance_and_time

from .services import machine_list
from .serializers import MachineSerializer, RecycleLogSerializer, FilterSerializer
from .models import Machine, RecycleLog

class Machines(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = MachineSerializer

    def get_queryset(self):
        filters_serializer = FilterSerializer(data=self.request.query_params)
        filters_serializer.is_valid(raise_exception=True)
        machines = machine_list(filters=filters_serializer.validated_data)
        machines = machines.order_by("-ordering")
        return machines

    def get_permissions(self):
        self.action = self.request.method
        if self.action.lower() == "post":
            return [IsAdminUser()]
        return [IsAuthenticated()]

    @extend_schema(parameters=[OpenApiParameter(name="identification_name", location=OpenApiParameter.QUERY, description="machine name", required=False,type=str),
                               OpenApiParameter(name="city",location=OpenApiParameter.QUERY,description="machine city",required=False,type=str),
                               OpenApiParameter(name="place",location=OpenApiParameter.QUERY,description="machine address",required=False,type=str)])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

class MachinePage(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = MachineSerializer

    def get_queryset(self):
        filters_serializer = FilterSerializer(data=self.request.query_params)
        filters_serializer.is_valid(raise_exception=True)
        machines = machine_list(filters=filters_serializer.validated_data)
        machines = machines.order_by("-ordering")
        return machines

    @extend_schema(parameters=[OpenApiParameter(name="identification_name", location=OpenApiParameter.QUERY, description="machine name", required=False,type=str),
                               OpenApiParameter(name="city",location=OpenApiParameter.QUERY,description="machine city",required=False,type=str),
                               OpenApiParameter(name="place",location=OpenApiParameter.QUERY,description="machine address",required=False,type=str)])
    def get(self, request, long, lat, *args, **kwargs):
        current_location = Point(float(long), float(lat), srid=4326)
        machines_seriazlizer = self.serializer_class(self.get_queryset(), many=True, context={"current_location": current_location})
        nearest_machine = (Machine.objects.annotate(distance=Distance("location", current_location, spheroid=True)).order_by("distance").first())
        nearest_machine_serializer = MachineSerializer(nearest_machine, context={"current_location": current_location})
        return Response({
            "machines": machines_seriazlizer.data,
            "nearest_machine": nearest_machine_serializer.data
        }, status=200)

class MachineDetail(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Machine.objects.all()
    serializer_class = MachineSerializer

    def get_permissions(self):
        self.action = self.request.method
        if self.action.lower() == "put" or self.action.lower() == "patch":
            return [IsAdminUser()]
        return [IsAuthenticated()]

class MachineDelete(generics.DestroyAPIView):
    permission_classes = [IsAdminUser]
    queryset = Machine.objects.all()
    serializer_class = MachineSerializer

class RetrieveRecycleLog(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = RecycleLogSerializer

    def get(self, request, pk):
        logs = RecycleLog.objects.filter(user=request.user.id, is_complete=True)
        serializer = self.serializer_class(logs, many=True)
        return Response({
            "message": "Success",
            "data": serializer.data,
        })
