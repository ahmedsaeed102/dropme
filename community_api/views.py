from django.shortcuts import render
from .models import ChannelsModel
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.generics import ListAPIView, RetrieveAPIView, CreateAPIView, DestroyAPIView, UpdateAPIView
from .serializers import ChannelsCreateSerializer, ChannelsSerializer


def room(request, room_name):
    return render(request, "community_api/room.html", {"room_name": room_name})


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
    pass



class ImgUpload(APIView):
    pass


class VideoUpload(APIView):
    pass


# class FileUpload(APIView):
#     pass