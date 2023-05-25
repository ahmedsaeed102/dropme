from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.exceptions import NotFound
from firebase_admin.messaging import Message, Notification
from fcm_django.models import FCMDevice
from .serializers import MachineSerializer, RecycleLogSerializer
from .models import Machine, RecycleLog


class Machines(generics.ListCreateAPIView):
    """
    [GET] return all machines in database
    [Post] add new machine to database
    """

    permission_classes = [IsAuthenticated]
    queryset = Machine.objects.all()
    serializer_class = MachineSerializer

    def perform_create(self, serializer):
        # send notification to all user after a new machine is added
        serializer.save()
        FCMDevice.objects.send_message(
            Message(
                notification=Notification(
                    title="New Machine",
                    body="New Machine has been added, check it out!",
                )
            )
        )


class MachineDetail(generics.RetrieveUpdateAPIView):
    """
    given an id return machine details
    """

    permission_classes = [IsAuthenticated]
    queryset = Machine.objects.all()
    serializer_class = MachineSerializer


class MachineDelete(generics.DestroyAPIView):
    permission_classes = [IsAdminUser]
    queryset = Machine.objects.all()
    serializer_class = MachineSerializer


class RetrieveRecycleLog(APIView):
    """
    Retrieve the user's recycling logs
    """

    permission_classes = [IsAuthenticated]
    serializer_class = RecycleLogSerializer

    def get(self, request, pk):
        logs = RecycleLog.objects.filter(user=pk, is_complete=True)
        if not logs:
            raise NotFound(detail="Error 404, no logs for current user", code=404)

        serializer = RecycleLogSerializer(logs, many=True)

        return Response(
            {
                "message": "Success",
                "data": serializer.data,
            }
        )
