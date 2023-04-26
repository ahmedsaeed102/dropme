from django.shortcuts import render,get_object_or_404
from django.shortcuts import get_object_or_404
from community_api.models import ChannelsModel, UserModel,MessagesModel
from .serializers import ChannelsCreateSerializer,ChannelsSerializer

# chat/views.py
from rest_framework import permissions
from rest_framework.generics import (
    ListAPIView,
    RetrieveAPIView,
    CreateAPIView,
    DestroyAPIView,
    UpdateAPIView
)



def index(request):
    return render(request, "community_api/index.html")

def room(request, room_name):
    return render(request, "community_api/room.html", {"room_name": room_name})




class ChannelsListView(ListAPIView):
    queryset = ChannelsModel.objects.all()
    serializer_class = ChannelsSerializer
    permission_classes = (permissions.AllowAny, )
    # def get_queryset(self):
    #     queryset = ChannelsModel.objects.all()
    #     username = self.request.query_params.get('username', None)
    #     if username is not None:
    #         channels = get_user_channel(username)
    #         queryset = channels.chats.all()
    #     return queryset


class ChannelsDetailView(RetrieveAPIView):
    queryset = ChannelsModel.objects.all()
    serializer_class = ChannelsSerializer
    permission_classes = (permissions.AllowAny, )


class ChannelsCreateView(CreateAPIView):
    queryset = ChannelsModel.objects.all()
    serializer_class = ChannelsCreateSerializer
    permission_classes = (permissions.IsAuthenticated, )
    # permissions.IsAdminUser,


class ChannelsUpdateView(UpdateAPIView):
    queryset = ChannelsModel.objects.all()
    serializer_class = ChannelsSerializer
    permission_classes = (permissions.IsAuthenticated, )


class ChannelsDeleteView(DestroyAPIView):
    queryset = ChannelsModel.objects.all()
    serializer_class = ChannelsSerializer
    permission_classes = (permissions.IsAuthenticated, )
    # permissions.IsAdminUser,



def last_10_messages(channels_id):
    """ return the last recent 10 messages """
    channels_chat=get_object_or_404(ChannelsModel,id=channels_id)
    return channels_chat.messages.objects.order_by('-message_dt').all()[:10]

def get_current_chat(channels_id):
    """ return the current chat"""
    return get_object_or_404(ChannelsModel,id=channels_id)


def get_user_channel(username):
    """ retrive user data inside specific channels"""
    user=get_object_or_404(UserModel,username)
    channels=get_object_or_404(ChannelsModel,participants=user)
    return channels