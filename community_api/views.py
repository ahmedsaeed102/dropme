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
from drf_spectacular.utils import extend_schema
from .models import ChannelsModel, MessagesModel
from .utlis import *
from .serializers import *


def room(request, room_name):
    return render(request, "community_api/room.html", {"room_name": room_name})


class MessagesPagination(PageNumberPagination):
    page_size = 5


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

    def perform_create(self, serializer):
        # send notification to all user after a new channel is created
        serializer.save()
        send_new_community_notification(serializer.data['room_name'])


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
    

class SendTextMessage(APIView):
    serializer_class = TextMessageSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request, room_name):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            # create msg and save it
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
            send_community_notification(room_name)

            return Response('message sent successfully', status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(request={'multipart/form-data': {'type': 'object','properties': {'img': {'type': 'string','format': 'binary'}}}}) 
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
            send_community_notification(room_name)

            return Response('Image sent successfully', status=status.HTTP_201_CREATED)
        
        except Exception as e:
                return Response({'message':str(e)}, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(request={'multipart/form-data': {'type': 'object', 'properties': {'video': {'type': 'string', 'format': 'binary'}}}}) 
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
            send_community_notification(room_name)
            
            return Response('video sent successfully', status=status.HTTP_201_CREATED)
        
        except Exception as e:
                return Response({'message':str(e)}, status=status.HTTP_400_BAD_REQUEST)


class SendReactionMessage(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = SendReactionSerializer

    def patch(self, request, room_name):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            # get msg and update it
            msg = MessagesModel.objects.get(id=serializer.data['message_id'])

            emoji = serializer.data['emoji']
            if emoji not in msg.reactions:
                msg.reactions[emoji] = {'count':1, 'users':[request.user.id]}
            else:
                if request.user.id not in msg.reactions[emoji]['users']:
                    msg.reactions[emoji]['count'] += 1
                    msg.reactions[emoji]['users'].append(request.user.id)
                else:
                    return Response('you already reacted to this message', status=status.HTTP_400_BAD_REQUEST)
            
            msg.save()

            # send reaction to all users in room
            channel_layer = get_channel_layer()
            msg = ReactionSerializer(msg)
          
            try:
                async_to_sync(channel_layer.group_send)(room_name,{
                    "type": "send.messages",
                    'message_type':'reaction',
                    'data':msg.data,
                })

            except Exception as e:
                return Response({'message':str(e)}, status=status.HTTP_400_BAD_REQUEST)

            return Response('reaction sent successfully', status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RemoveReactionMessage(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = SendReactionSerializer

    def patch(self, request, room_name):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            # get msg and update it
            msg = MessagesModel.objects.get(id=serializer.data['message_id'])

            emoji = serializer.data['emoji']
            if emoji not in msg.reactions:
                return Response('reaction does not exist', status=status.HTTP_400_BAD_REQUEST)
            else:
                if request.user.id in msg.reactions[emoji]['users']:
                    msg.reactions[emoji]['count'] -= 1
                    msg.reactions[emoji]['users'].remove(request.user.id)
                else:
                    return Response('this user did not react to this message', status=status.HTTP_400_BAD_REQUEST)
            
            msg.save()

            # send update to all users in room
            channel_layer = get_channel_layer()
            msg = ReactionSerializer(msg)
          
            try:
                async_to_sync(channel_layer.group_send)(room_name,{
                    "type": "send.messages",
                    'message_type':'reaction',
                    'data':msg.data,
                })

            except Exception as e:
                return Response({'message':str(e)}, status=status.HTTP_400_BAD_REQUEST)

            return Response('reaction removed successfully', status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)