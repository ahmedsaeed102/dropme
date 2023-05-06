from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.generics import ListAPIView, RetrieveAPIView, CreateAPIView, DestroyAPIView, UpdateAPIView
from rest_framework.pagination import PageNumberPagination
from .models import ChannelsModel
from .utlis import get_current_chat
from .serializers import ChannelsCreateSerializer, ChannelsSerializer, MessagesSerializer


def room(request, room_name):
    return render(request, "community_api/room.html", {"room_name": room_name})

class MessagesPagination(PageNumberPagination):
    page_size = 20


class ChannelsListView(ListAPIView):
    queryset = ChannelsModel.objects.all()
    serializer_class = ChannelsSerializer


class ChannelsDetailView(RetrieveAPIView):
    queryset = ChannelsModel.objects.all()
    serializer_class = ChannelsSerializer
    permission_classes = (IsAuthenticated,)


class ChannelsCreateView(CreateAPIView):
    queryset = ChannelsModel.objects.all()
    serializer_class = ChannelsCreateSerializer
    permission_classes = (IsAdminUser,)


class ChannelsUpdateView(UpdateAPIView):
    queryset = ChannelsModel.objects.all()
    serializer_class = ChannelsSerializer
    permission_classes = (IsAuthenticated,)


class ChannelsDeleteView(DestroyAPIView):
    queryset = ChannelsModel.objects.all()
    serializer_class = ChannelsSerializer
    permission_classes = (IsAdminUser,)


class ChannelMessages(ListAPIView):
    serializer_class = MessagesSerializer
    lookup_url_kwarg = "room_name"
    pagination_class = MessagesPagination

    def get_queryset(self):
        room = self.kwargs.get(self.lookup_url_kwarg)
        channel = get_current_chat(room)
        messages = channel.messages.all()
        return messages


class ImgUpload(APIView):
    pass


class VideoUpload(APIView):
    pass


# class FileUpload(APIView):
#     pass