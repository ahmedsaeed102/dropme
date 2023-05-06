from django.shortcuts import get_object_or_404
from .models import ChannelsModel, UserModel


def last_10_messages(room_name):
    """ return the last recent 10 messages """

    channels_chat = get_object_or_404(ChannelsModel, room_name=room_name)

    return channels_chat.messages.objects.order_by('-message_dt').all()[:10]


def get_current_chat(room_name):
    """ return the current chat"""

    return get_object_or_404(ChannelsModel, room_name=room_name)


def get_user_channel(username):
    """ retrive user data inside specific channels"""

    user=get_object_or_404(UserModel, username)
    channels=get_object_or_404(ChannelsModel, participants=user)
    return channels