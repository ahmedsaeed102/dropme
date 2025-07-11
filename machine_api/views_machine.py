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
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework_api_key.permissions import HasAPIKey

from users_api.models import UserModel
from users_api.serializers import UserSerializer
from notification.services import notification_send, fcmdevice_get
from .serializers import QRCodeSerializer, UpdateRecycleLog, MachineVideoSerializer
from .models import Machine, RecycleLog, PhoneNumber, MachineVideo
from .utlis import update_user_points, calculate_points
from notification.models import NotificationImage

class MachineQRCode(APIView):
    permission_classes = [HasAPIKey | IsAuthenticated]
    serializer_class = QRCodeSerializer

    def get(self, request, name):
        try:
            machine = Machine.objects.get(identification_name=name)
        except Machine.DoesNotExist:
            raise NotFound(detail="Error 404, Machine not found", code=404)

        path = request.build_absolute_uri(reverse("start_recycle", kwargs={"name": machine.identification_name}))
        path = path.replace("http", "ws")
        qrcode_img = qrcode.make(path)
        fname = f"qr_code-{machine.identification_name}.png"
        buffer = BytesIO()
        qrcode_img.save(buffer, "PNG")
        machine.qr_code.save(fname, File(buffer), save=True)
        return HttpResponse(machine.qr_code, content_type="image/png")

class MachineVideos(APIView):
    permission_classes = [HasAPIKey | IsAuthenticated]
    serializer_class = MachineVideoSerializer

    def get(self, request):
        videos = MachineVideo.objects.all()
        serializer = self.serializer_class(videos, many=True)
        return Response(serializer.data)

class IsMachineBusy(APIView):
    permission_classes = [HasAPIKey]

    def get(self, request, name):
        logs = RecycleLog.objects.filter(machine_name=name, in_progess=True)
        if not logs:
            return Response({"message": "no user logged in", "busy": False})

        user = UserSerializer(logs[0].user)
        user = user.data
        user["total_points"] = logs[0].user.total_points
        return Response({"message": "User logged in", "busy": True, "user": user})

class MachineIsFull(APIView):
    permission_classes = [HasAPIKey]

    def get(self, request, name):
        machine = Machine.objects.get(identification_name=name)
        machine.status = "breakdown"
        machine.status_ar = "لا تعمل"
        machine.save()

        admin_users = UserModel.objects.filter(is_staff=True)
        devices = fcmdevice_get(user__in=admin_users)
        if NotificationImage.objects.filter(name="full_machine").exists():
            image = NotificationImage.objects.filter(name="full_machine").first().image
        else:
            image = None
        notification_send(
            devices=devices,
            users = admin_users,
            title="Machine is full",
            body=f"{name} machine is full empty it!",
            title_ar="الماكينة ممتلئة",
            body_ar=f" ماكينة {name} ممتلئة قم بتفريغها!",
            image=image,
            type="machine",
            extra_data={"room_name": None, "id": machine.id, "extra":None}
        )

        subject = "Machine is full"
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [ user.email for user in admin_users ]
        send_mail(subject, f"Machine {name} is full", email_from, recipient_list)
        return Response({"message": "Admin notified successfully"})

class CheckRecycle(APIView):
    permission_classes = [HasAPIKey | IsAdminUser]

    def get(self, request, name):
        log = (RecycleLog.objects.filter(machine_name=name, in_progess=True).order_by("-created_at").first())
        if log:
            return Response({"log": True}, status=200)
        return Response({"log": False}, status=200)

class UpdateV2Recycle(APIView):
    permission_classes = [HasAPIKey | IsAdminUser]
    serializer_class = UpdateRecycleLog

    def post(self, request, name):
        bottles = request.data.get("bottles", 0)
        cans = request.data.get("cans", 0)
        print("UpdateV2Recycle", name, bottles, cans, request.data)
        log = (RecycleLog.objects.filter(machine_name=name, in_progess=True).order_by("-created_at").first())
        if not log:
            raise NotFound(detail="Error 404, log not found", code=404)

        _, _, total_points = calculate_points(bottles, cans)
        log.bottles += bottles
        log.cans += cans
        log.save()
        channel_layer = get_channel_layer()
        if bottles == 0 and cans == 0:
            message = "you have not thrown any bottle or can"
            message_ar = "لم تقم برمي أي زجاجة أو علبة"
        elif bottles != 0 and cans == 0:
            message = f"you have thrown {bottles} bottles with {total_points} points" 
            message_ar = f"لقد قمت برمي {bottles} زجاجة بنقاط {total_points}"
        elif bottles == 0 and cans != 0:
            message = f"you have thrown {cans} cans with {total_points} points"
            message_ar = f"لقد قمت برمي {cans} علبة بنقاط {total_points}"
        else:
            message = f"you have thrown {bottles} bottles and {cans} cans with {total_points} points"
            message_ar = f"لقد قمت برمي {bottles} زجاجة و {cans} علبة بنقاط {total_points}"
        try:
            async_to_sync(channel_layer.send)(
                log.channel_name,
                {
                    "type": "receive.update",
                    "message": message,
                    "message_ar": message_ar,
                }
            )
        except Exception as e:
            return Response({"message": "error in sending update to user mobile phone"})
        return Response({"message": "success", "points": total_points})

class FinishRecycle(APIView):
    permission_classes = [HasAPIKey | IsAdminUser]

    def post(self, request, name):
        print("FinishRecycle", request.data)
        log = (RecycleLog.objects.filter(machine_name=name, in_progess=True).order_by("-created_at").first())
        if not log:
            raise NotFound(detail="Error 404, log not found", code=404)

        bottles = log.bottles
        cans = log.cans

        _, _, total_points = calculate_points(bottles, cans)
        log.points = total_points
        log.in_progess = False
        log.is_complete = True
        log.save()
        update_user_points(log.user.id, total_points)
        channel_layer = get_channel_layer()
        for i in range(3):
            try:
                print("start finish")
                async_to_sync(channel_layer.send)(
                    log.channel_name,
                    {
                        "type": "receive.update",
                        "bottles": log.bottles,
                        "cans": log.cans,
                        "points": log.points,
                    })
                print("done syncing")
            except Exception as e:
                print("error in sending update to user mobile phone", e)
                if i == 0:
                    return Response({"message": "error in sending update to user mobile phone"})
        return Response({"message": "success", "points": total_points})

class UpdateRecycle(APIView):
    """
    The machine should send a request to this endpoint with the number of items recycled
    data schema: {
    bottles: int,
    cans: int
    }
    """

    permission_classes = [HasAPIKey | IsAdminUser]
    serializer_class = UpdateRecycleLog

    def post(self, request, name):
        print("starting update")
        bottles = request.data.get("bottles", 0)
        cans = request.data.get("cans", 0)
        print("UpdateRecycle", name, bottles, cans, request.data)
        log = (
            RecycleLog.objects.filter(machine_name=name, in_progess=True)
            .order_by("-created_at")
            .first()
        )

        if not log:
            raise NotFound(detail="Error 404, log not found", code=404)

        _, _, total_points = calculate_points(bottles, cans)

        log.bottles = bottles
        log.cans = cans
        log.points = total_points
        log.in_progess = False
        log.is_complete = True
        log.save()
        channel_layer = get_channel_layer()

        update_user_points(log.user.id, total_points)

        print("done update")
        # try 3 times
        for i in range(3):
            try:
                print("send to app")
                async_to_sync(channel_layer.send)(
                    log.channel_name,
                    {
                        "type": "receive.update",
                        "bottles": log.bottles,
                        "cans": log.cans,
                        "points": log.points,
                    },
                )
                print("done syncing")
            except Exception as e:
                print("error in sending update to user mobile phone", e)
                if i == 0:
                    return Response({"message": "error in sending update to user mobile phone"})

        return Response({"message": "success", "points": total_points})

class RecycleWithPhoneNumber(APIView):
    permission_classes = [HasAPIKey | IsAdminUser]
    serializer_class = UpdateRecycleLog

    def post(self, request, name, phone_number):
        bottles = request.data.get("bottles", 0)
        cans = request.data.get("cans", 0)
        phone_number = phone_number.lstrip("0")
        print("RecycleWithPhoneNumber", phone_number, bottles, cans)
        phone, created = PhoneNumber.objects.get_or_create(phone_number=phone_number)
        machine = Machine.objects.filter(identification_name=name).first()
        _, _, total_points = calculate_points(bottles, cans)
        user = UserModel.objects.filter(phone_number=phone_number).first()
        if user:
            RecycleLog.objects.create(machine_name=name, user=user, bottles=bottles, cans=cans, points=total_points, is_complete=True, machine=machine)
            update_user_points(user.id, total_points)
        else:
            RecycleLog.objects.create(machine_name=name, phone=phone, bottles=bottles, cans=cans, points=total_points, is_complete=True, machine=machine)
            phone.points += total_points
            phone.save()
        return Response({"message": "success", "points": total_points})