from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.generics import ListAPIView, RetrieveAPIView, CreateAPIView, DestroyAPIView, UpdateAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser
from .models import ChannelsModel, MessagesModel
from .utlis import get_current_chat
from .serializers import *


def room(request, room_name):
    return render(request, "community_api/room.html", {"room_name": room_name})

#-----------------------CRUD------------------------------

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
    
#-----------------------------------------------------------------------------------


class SendTextMessage(APIView):
    serializer_class = TextMessageSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request, room_name):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            # create msg and save it
            # content=**serializer.data['content']
            msg = MessagesModel.objects.create(user_model=request.user, **serializer.data)
            current_chat=get_current_chat(room_name)
            current_chat.messages.add(msg)
            current_chat.save()

            # send msg to all users in room
            channel_layer = get_channel_layer()
            msg = MessagesSerializer(msg)
          
            try:
                async_to_sync(channel_layer.group_send)(room_name,{
                    "type": "send.messages",
                    'message_type':'text',
                    'data':msg.data,
                })

            except Exception as e:
                return Response({'message':str(e)}, status=status.HTTP_400_BAD_REQUEST)
            
            # send notification

            return Response('message sent successfully', status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SendImgMessage(APIView):
    permission_classes = (IsAuthenticated,)
    parser_classes = (MultiPartParser,)
    serializer_class = ImgUploadSerializer

    def post(self, request, room_name):
        try:
            msg = MessagesModel.objects.create(user_model=request.user, img=request.FILES['img'])
            current_chat=get_current_chat(room_name)
            current_chat.messages.add(msg)
            current_chat.save()

            # send msg to all users in room
            channel_layer = get_channel_layer()
            msg = MessagesSerializer(msg)
            async_to_sync(channel_layer.group_send)(room_name,{
                    "type": "send.messages",
                    'message_type':'img',
                    'data':msg.data,
            })

            # send notification

            return Response('Image sent successfully', status=status.HTTP_201_CREATED)
        
        except Exception as e:
                return Response({'message':str(e)}, status=status.HTTP_400_BAD_REQUEST)


class SendVideoMessage(APIView):
    permission_classes = (IsAuthenticated,)
    parser_classes = (MultiPartParser,)
    serializer_class = VideoUploadSerializer

    def post(self, request, room_name):
        try:
            msg = MessagesModel.objects.create(user_model=request.user, video=request.FILES['video'])
            current_chat=get_current_chat(room_name)
            current_chat.messages.add(msg)
            current_chat.save()

            # send msg to all users in room
            channel_layer = get_channel_layer()
            msg = MessagesSerializer(msg)
            async_to_sync(channel_layer.group_send)(room_name,{
                    "type": "send.messages",
                    'message_type':'video',
                    'data':msg.data,
            })

            # send notification

            return Response('video sent successfully', status=status.HTTP_201_CREATED)
        
        except Exception as e:
                return Response({'message':str(e)}, status=status.HTTP_400_BAD_REQUEST)