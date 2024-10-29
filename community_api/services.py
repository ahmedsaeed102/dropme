from django.shortcuts import get_object_or_404
from django.db import transaction
from asgiref.sync import async_to_sync
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import APIException, NotFound, ValidationError, PermissionDenied
from channels.layers import get_channel_layer

from notification.services import notification_send, fcmdevice_get, fcmdevice_get_all
from .models import ChannelsModel, MessagesModel, ReportModel, CommentsModel
from .utlis import check_if_user_reacted_to_message, check_if_user_reacted_to_comment

User = get_user_model()

def community_get(*, room_name: str) -> ChannelsModel:
    return get_object_or_404(ChannelsModel, room_name=room_name)

def message_get(*, message_id: int) -> MessagesModel:
    return get_object_or_404(MessagesModel, pk=message_id)

def comment_get(*, comment_id: int) -> CommentsModel:
    return get_object_or_404(CommentsModel, pk=comment_id)

def user_reaction_get(*, model, user_id):
    reactions = model.reactions
    for reaction, value in reactions.items():
        if user_id in value["users_ids"]:
            return reaction
    return ""

class Message:
    @staticmethod
    def is_a_participant(room: ChannelsModel, user) -> bool:
        if room.channel_type == "private" and user not in room.users.all():
            raise PermissionDenied({"detail": _("You are not a participant in this channel")})
        return True

    @transaction.atomic
    @staticmethod
    def new_message_create(*, request, room: ChannelsModel, message_content: str) -> MessagesModel:
        new_message = MessagesModel.objects.create(user_model=request.user, content=message_content, img=request.FILES.get("img", None), video=request.FILES.get("video", None))
        room.messages.add(new_message)
        room.save()
        return new_message

    @staticmethod
    def new_message_send(*, room_name, message, message_type) -> None:
        try:
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(room_name,{"type": "send.messages","message_type": message_type,"data": message})
        except Exception as e:
            raise APIException(str(e))

    @staticmethod
    def new_message_notification_send(*, request, room_type, room) -> None:
        if room_type == "public":
            notification_off_users = ChannelsModel.objects.values_list('notification_off_users', flat=True).distinct()
            devices = fcmdevice_get_all().exclude(user__id__in=notification_off_users).exclude(user=request.user.pk)
            users = User.objects.exclude(id__in=notification_off_users).exclude(id=request.user.pk)
        else:
            devices = fcmdevice_get(user__user_channels__room_name=room.room_name).exclude(id__in=room.notification_off_users.values_list('id', flat=True)).exclude(id=request.user.pk)
            users = room.users.exclude(id__in=room.notification_off_users.values_list('id', flat=True)).exclude(id=request.user.pk)
        notification_send(
            devices=devices,
            users = users,
            title="New message",
            body=f"""You have a new message in '{room.room_name}' community channel""",
            title_ar="رسالة جديدة",
            body_ar=f"لديك رسالة جديدة في قناة المجتمع '{room.room_name_ar}'"
        )

    @staticmethod
    def message_reaction_add(*, emoji: str, message: MessagesModel, user_id: int) -> MessagesModel:
        if emoji not in message.reactions:
            raise NotFound({"detail": _("Emoji not found")})
        else:
            if not check_if_user_reacted_to_message(message.reactions, user_id):
                message.reactions[emoji]["count"] += 1
                message.reactions[emoji]["users_ids"].append(user_id)
                message.reactions[emoji]["users"].append({"id": user_id, "reaction": emoji})
                message.save()
            else:
                raise ValidationError({"detail": _("You already reacted to this message")})
        return message

    @staticmethod
    def message_reaction_remove(*, emoji: str, message: MessagesModel, user_id: int) -> MessagesModel:
        if emoji not in message.reactions:
            raise NotFound({"detail:": _("Emoji not found")})
        else:
            if user_id in message.reactions[emoji]["users_ids"]:
                message.reactions[emoji]["count"] -= 1
                message.reactions[emoji]["users_ids"].remove(user_id)
                message.reactions[emoji]["users"] = [dictionary for dictionary in message.reactions[emoji]["users"] if dictionary.get("id") != user_id]
                message.save()
            else:
                raise ValidationError({"detail": _("You haven't reacted using this emoji")})
        return message

    @transaction.atomic
    @staticmethod
    def message_reaction_change(*, old_emoji: str, new_emoji: str, message: MessagesModel, user_id: int) -> MessagesModel:
        message = Message.message_reaction_remove(emoji=old_emoji, message=message, user_id=user_id)
        message = Message.message_reaction_add(emoji=new_emoji, message=message, user_id=user_id)
        return message

class Comment:

    @staticmethod
    def comment_reaction_add(*, emoji: str, comment: CommentsModel, user_id: int) -> CommentsModel:
        if emoji not in comment.reactions:
            raise NotFound({"detail": _("Emoji not found")})
        else:
            if not check_if_user_reacted_to_comment(comment.reactions, user_id):
                comment.reactions[emoji]["count"] += 1
                comment.reactions[emoji]["users_ids"].append(user_id)
                comment.reactions[emoji]["users"].append({"id": user_id, "reaction": emoji})
                comment.save()
            else:
                raise ValidationError({"detail": _("You already reacted to this comment")})
        return comment

    @staticmethod
    def comment_reaction_remove(*, emoji: str, comment: CommentsModel, user_id: int) -> CommentsModel:
        if emoji not in comment.reactions:
            raise NotFound({"detail:": _("Emoji not found")})
        else:
            if user_id in comment.reactions[emoji]["users_ids"]:
                comment.reactions[emoji]["count"] -= 1
                comment.reactions[emoji]["users_ids"].remove(user_id)
                comment.reactions[emoji]["users"] = [dictionary for dictionary in comment.reactions[emoji]["users"] if dictionary.get("id") != user_id]
                comment.save()
            else:
                raise ValidationError({"detail": _("You haven't reacted using this emoji")})
        return comment

    @transaction.atomic
    @staticmethod
    def comment_reaction_change(*, old_emoji: str, new_emoji: str, comment: CommentsModel, user_id: int) -> CommentsModel:
        comment = Comment.comment_reaction_remove(emoji=old_emoji, comment=comment, user_id=user_id)
        comment = Comment.comment_reaction_add(emoji=new_emoji, comment=comment, user_id=user_id)
        return comment

def report_create(*, request, message_id: int) -> ReportModel:
    try:
        msg = message_get(message_id=message_id)
        report = ReportModel.objects.create(reporter=request.user, reported_message=msg)
    except Exception as e:
        raise APIException(str(e))
    return report
