from firebase_admin.messaging import Message, Notification
from fcm_django.models import FCMDevice
from .models import Notification as NotificaitonModel


def notification_create(*, devices: list[FCMDevice], title: str, body: str) -> None:
    NotificaitonModel.objects.bulk_create(
        [
            NotificaitonModel(user=device.user, title=title, body=body)
            for device in devices
        ]
    )


def notification_send_all(*, title: str, body: str) -> None:
    FCMDevice.objects.send_message(
        Message(
            notification=Notification(
                title=title,
                body=body,
            )
        )
    )

    notification_create(devices=FCMDevice.objects.all(), title=title, body=body)


def notification_send_by_name(*, name: str, title: str, body: str) -> None:
    device = FCMDevice.objects.get(name=name)

    device.send_message(
        Message(
            notification=Notification(
                title=title,
                body=body,
            )
        )
    )

    notification_create(devices=[device], title=title, body=body)
