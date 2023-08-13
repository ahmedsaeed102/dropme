from django.shortcuts import get_object_or_404
from django.db import transaction
from asgiref.sync import async_to_sync
from rest_framework.exceptions import APIException, NotFound, ValidationError
from channels.layers import get_channel_layer
from notification.services import notification_send, fcmdevice_get, fcmdevice_get_all
from .models import ChannelsModel, MessagesModel, ReportModel
from .utlis import check_if_user_reacted_to_message


def community_get(*, room_name: str) -> ChannelsModel:
    return get_object_or_404(ChannelsModel, room_name=room_name)


def message_get(*, message_id: int) -> MessagesModel:
    return get_object_or_404(MessagesModel, pk=message_id)


class Message:
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
        try:
            channel_layer = get_channel_layer()

            async_to_sync(channel_layer.group_send)(
                room_name,
                {
                    "type": "send.messages",
                    "message_type": message_type,
                    "data": message,
                },
            )
        except Exception as e:
            raise APIException(str(e))

    @staticmethod
    def message_reaction_add(
        *, emoji: str, message: MessagesModel, user_id: int
    ) -> MessagesModel:
        if emoji not in message.reactions:
            raise NotFound("Emoji not found")
        else:
            if not check_if_user_reacted_to_message(message.reactions, user_id):
                message.reactions[emoji]["count"] += 1
                message.reactions[emoji]["users_ids"].append(user_id)
                message.reactions[emoji]["users"].append(
                    {"id": user_id, "reaction": emoji}
                )
                message.save()
            else:
                raise ValidationError({"detail": "You already reacted to this message"})

        return message

    @staticmethod
    def message_reaction_remove(
        *, emoji: str, message: MessagesModel, user_id: int
    ) -> MessagesModel:
        if emoji not in message.reactions:
            raise NotFound("Emoji not found")
        else:
            if user_id in message.reactions[emoji]["users_ids"]:
                message.reactions[emoji]["count"] -= 1
                message.reactions[emoji]["users_ids"].remove(user_id)
                message.reactions[emoji]["users"] = [
                    dictionary
                    for dictionary in message.reactions[emoji]["users"]
                    if dictionary.get("id") != user_id
                ]
                message.save()
            else:
                raise ValidationError(
                    {"detail": "You haven't reacted using this emoji"}
                )

        return message

    @transaction.atomic
    @staticmethod
    def message_reaction_change(
        *, old_emoji: str, new_emoji: str, message: MessagesModel, user_id: int
    ) -> MessagesModel:
        # remove old emoji from message
        message = Message.message_reaction_remove(
            emoji=old_emoji, message=message, user_id=user_id
        )

        # add new emoji to message
        message = Message.message_reaction_add(
            emoji=new_emoji, message=message, user_id=user_id
        )

        return message

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


def report_create(*, request, message_id: int) -> ReportModel:
    try:
        msg = message_get(message_id=message_id)
        report = ReportModel.objects.create(reporter=request.user, reported_message=msg)
    except Exception as e:
        raise APIException(str(e))

    return report
