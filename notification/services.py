from firebase_admin.messaging import Message, Notification
from fcm_django.models import FCMDevice, FCMDeviceQuerySet

from .models import Notification as NotificaitonModel
from users_api.models import UserModel

def fcmdevice_get(**kwargs) -> FCMDeviceQuerySet:
    return FCMDevice.objects.filter(**kwargs)

def fcmdevice_get_all() -> FCMDeviceQuerySet:
    return FCMDevice.objects.all()

def notification_create(*, users, title, body, title_ar, body_ar) -> None:
    NotificaitonModel.objects.bulk_create([NotificaitonModel(user=user, title_en=title, body_en=body, title_ar=title_ar, body_ar=body_ar) for user in users])

def notification_send_all(*, title: str, body: str, title_ar:str, body_ar:str) -> None:
    FCMDevice.objects.send_message(Message(notification=Notification(title=title, body=body)))
    users = UserModel.objects.all()
    notification_create(users=users, title=title, body=body, title_ar=title_ar, body_ar=body_ar)

def notification_send(*, devices, users, title, body, title_ar, body_ar) -> None:
    devices.send_message(Message(notification=Notification(title=title, body=body)))
    notification_create(users=users, title=title, body=body, title_ar=title_ar, body_ar=body_ar)

def notification_send_by_name(*, name: str, title: str, body: str, title_ar:str, body_ar:str) -> None:
    device = FCMDevice.objects.filter(name=name).first()
    if device:
        device.send_message(Message(notification=Notification(title=title, body=body)))
    user = UserModel.objects.filter(username=name)
    notification_create(users=user, title=title, body=body,  title_ar=title_ar, body_ar=body_ar)
