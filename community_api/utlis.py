from django.shortcuts import get_object_or_404
from firebase_admin.messaging import Message, Notification
from fcm_django.models import FCMDevice
from .models import ChannelsModel, UserModel


def get_current_chat(room_name):
    """ return the current chat"""

    return get_object_or_404(ChannelsModel, room_name=room_name)

def send_community_notification(room_name):
    FCMDevice.objects.send_message(
        Message(
            notification=Notification(
            title="New message", 
            body=f"You have a new message in '{room_name}' community channel", 
            )
        )
    )