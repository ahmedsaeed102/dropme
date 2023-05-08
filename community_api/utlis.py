from django.shortcuts import get_object_or_404
from .models import ChannelsModel, UserModel


def get_current_chat(room_name):
    """ return the current chat"""

    return get_object_or_404(ChannelsModel, room_name=room_name)

def send_community_notification():
    pass


# def get_user_channel(username):
#     """ retrive user data inside specific channels"""

#     user=get_object_or_404(UserModel, username)
#     channels=get_object_or_404(ChannelsModel, participants=user)
#     return channels