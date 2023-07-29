from django.shortcuts import get_object_or_404
from .models import ChannelsModel


def get_current_chat(room_name):
    return get_object_or_404(ChannelsModel, room_name=room_name)
