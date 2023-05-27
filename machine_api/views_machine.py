import qrcode
from io import BytesIO
from asgiref.sync import async_to_sync
from django.conf import settings
from django.http import HttpResponse
from django.urls import reverse
from django.core.files import File
from django.core.mail import send_mail
from channels.layers import get_channel_layer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAdminUser
from rest_framework_api_key.permissions import HasAPIKey
from firebase_admin.messaging import Message, Notification
from fcm_django.models import FCMDevice
from users_api.models import UserModel
from users_api.serializers import UserSerializer
from .serializers import QRCodeSerializer, UpdateRecycleLog
from .models import Machine, RecycleLog, PhoneNumber


class MachineQRCode(APIView):
    """
    Returns a QR code for the given machine name
    """

    permission_classes = [HasAPIKey | IsAdminUser]
    serializer_class = QRCodeSerializer

    def get(self, request, name):
        try:
            machine = Machine.objects.get(identification_name=name)
        except Machine.DoesNotExist:
            raise NotFound(detail="Error 404, Machine not found", code=404)

        path = request.build_absolute_uri(
            reverse("start_recycle", kwargs={"name": machine.identification_name})
        )
        path = path.replace("http", "ws")
        qrcode_img = qrcode.make(path)
        fname = f"qr_code-{machine.identification_name}.png"
        buffer = BytesIO()
        qrcode_img.save(buffer, "PNG")
        machine.qr_code.save(fname, File(buffer), save=True)

        return HttpResponse(machine.qr_code, content_type="image/png")


class IsMachineBusy(APIView):
    """
    Tells the machine if the user logedin using the QR Code or not.
    """

    permission_classes = [HasAPIKey]

    def get(self, request, name):
        logs = RecycleLog.objects.filter(machine_name=name, in_progess=True)
        if not logs:
            return Response(
                {
                    "message": "no user logged in",
                    "busy": False,
                }
            )

        user = UserSerializer(logs[0].user)
        user = user.data
        user["total_points"] = logs[0].user.total_points

        return Response(
            {
                "message": "User logged in",
                "busy": True,
                "user": user,
            }
        )


class MachineIsFull(APIView):
    permission_classes = [HasAPIKey]

    def get(self, request, name):
        machine = Machine.objects.get(identification_name=name)
        machine.status = "breakdown"
        machine.status_ar = "لا تعمل"
        machine.save()

        FCMDevice.objects.get(name="admin").send_message(
            Message(
                notification=Notification(
                    title="Machine is full",
                    body=f"{name} machine is full empty it!",
                )
            )
        )

        subject = "Machine is full"
        email_from = settings.EMAIL_HOST_USER
        to = UserModel.objects.get(username="admin").email
        recipient_list = [to]

        send_mail(
            subject,
            f"Machine {name} is full",
            email_from,
            recipient_list,
        )

        return Response(
            {
                "message": "Admin notified successfully",
            }
        )


class UpdateRecycle(APIView):
    """
    The machine should send a request to this endpoint with the number of items recycled
    data schema: {
    bottles: int,
    cans: int
    }
    """

    permission_classes = [HasAPIKey]
    serializer_class = UpdateRecycleLog

    def post(self, request, name):
        bottles = request.data.get("bottles", 0)
        cans = request.data.get("cans", 0)
        log = (
            RecycleLog.objects.filter(machine_name=name, in_progess=True)
            .order_by("-created_at")
            .first()
        )

        if not log:
            raise NotFound(detail="Error 404, log not found", code=404)

        points = (bottles + cans) * 10

        log.bottles = bottles
        log.cans = cans
        log.points = points
        log.in_progess = False
        log.is_complete = True
        log.save()
        channel_layer = get_channel_layer()

        try:
            async_to_sync(channel_layer.send)(
                log.channel_name,
                {
                    "type": "receive.update",
                    "bottles": log.bottles,
                    "cans": log.cans,
                    "points": log.points,
                },
            )

        except Exception as e:
            return Response({"message": "Points updated but user logged out"})

        return Response({"message": "success"})


class RecycleWithPhoneNumber(APIView):
    """
    Recycle using phone number
    The machine sends phone number and the number of items recycled
    """

    permission_classes = [HasAPIKey]
    serializer_class = UpdateRecycleLog

    def post(self, request, name, phone_number):
        bottles = request.data.get("bottles", 0)
        cans = request.data.get("cans", 0)

        phone, created = PhoneNumber.objects.get_or_create(phone_number=phone_number)

        points = (bottles + cans) * 10

        RecycleLog.objects.create(
            machine_name=name,
            phone=phone,
            bottles=bottles,
            cans=cans,
            points=points,
        )

        phone.points += points
        phone.save()

        return Response({"message": "success"})
