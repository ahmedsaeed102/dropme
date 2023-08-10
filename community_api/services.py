from django.shortcuts import get_object_or_404
from django.db import transaction
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from notification.services import notification_send, fcmdevice_get, fcmdevice_get_all
from .models import ChannelsModel, MessagesModel


def community_get(*, room_name: str) -> ChannelsModel:
    return get_object_or_404(ChannelsModel, room_name=room_name)


def message_get(*, message_id: int) -> MessagesModel:
    return get_object_or_404(MessagesModel, pk=message_id)


class NewMessage:
    @transaction.atomic
    @staticmethod
    def new_message_create(
        *, request, room: ChannelsModel, message_content: str
    ) -> MessagesModel:
        new_message = MessagesModel.objects.create(
            user_model=request.user,
            content=message_content,
            img=request.FILES.get("img", None),
            video=request.FILES.get("video", None),
        )

        room.messages.add(new_message)
        room.save()

        return new_message

    @staticmethod
    def new_message_send(*, room_name: str, message: dict, message_type: str) -> None:
        channel_layer = get_channel_layer()

        async_to_sync(channel_layer.group_send)(
            room_name,
            {
                "type": "send.messages",
                "message_type": message_type,
                "data": message,
            },
        )

    @staticmethod
    def new_message_notification_send(
        *, request, room_type: str, room_name: str
    ) -> None:
        if room_type == "public":
            devices = fcmdevice_get_all().exclude(user=request.user.pk)
            notification_send(
                devices=devices,
                title="New message",
                body=f"""You have a new message in '{room_name}' community channel""",
            )
        else:
            devices = fcmdevice_get(user__user_channels__room_name=room_name).exclude(
                user=request.user.pk
            )
            notification_send(
                devices=devices,
                title="New Message",
                body=f"""You have a new message in '{room_name}' community channel""",
            )
