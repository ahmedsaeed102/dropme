from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.shortcuts import render
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.generics import (
    ListAPIView,
    RetrieveAPIView,
    CreateAPIView,
    DestroyAPIView,
    UpdateAPIView,
)
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from drf_spectacular.utils import extend_schema
from notification.services import (
    notification_send_all,
    notification_send,
    fcmdevice_get,
    fcmdevice_get_all,
)
from users_api.services import send_email
from .models import ChannelsModel, MessagesModel, ReportModel
from .utlis import get_current_chat
from .serializers import *

User = get_user_model()


def room(request, room_name):
    return render(request, "community_api/room.html", {"room_name": room_name})


class MessagesPagination(PageNumberPagination):
    page_size = 5


class ChannelsListView(ListAPIView):
    queryset = ChannelsModel.objects.all()
    serializer_class = ChannelsSerializer
    permission_classes = (IsAuthenticated,)


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
        notification_send_all(
            title="New community channel",
            body=f"""A new community channel '{serializer.data["room_name"]}' has been created. check it out!""",
        )


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


@extend_schema(
    request={
        "multipart/form-data": {
            "type": "object",
            "properties": {
                "content": {"type": "string", "format": "string"},
                "img": {"type": "string", "format": "binary"},
                "video": {"type": "string", "format": "binary"},
            },
        }
    }
)
class SendMessage(APIView):
    serializer_class = SendMessageSerializer
    permission_classes = (IsAuthenticated,)
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, room_name):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            if not request.data:
                return Response("message is empty", status=status.HTTP_400_BAD_REQUEST)

            # create msg and save it
            msg = MessagesModel.objects.create(
                user_model=request.user,
                content=serializer.data["content"],
                img=request.FILES.get("img", None),
                video=request.FILES.get("video", None),
            )
            room = get_current_chat(room_name)
            room.messages.add(msg)
            room.save()

            # send msg to all users in room
            channel_layer = get_channel_layer()
            msg = MessagesSerializer(msg)

            try:
                async_to_sync(channel_layer.group_send)(
                    room_name,
                    {
                        "type": "send.messages",
                        "data": msg.data,
                    },
                )

            except Exception as e:
                return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

            # send notification
            if room.channel_type == "public":
                devices = fcmdevice_get_all(exclude=request.user.pk)
                notification_send(
                    devices=devices,
                    title="New message",
                    body=f"""You have a new message in '{room_name}' community channel""",
                )
            else:
                devices = fcmdevice_get(user__user_channels__room_name=room_name)
                notification_send(
                    devices=devices,
                    title="New Message",
                    body=f"""You have a new message in '{room_name}' community channel""",
                )

            return Response("message sent successfully", status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SendReactionMessage(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = SendReactionSerializer

    def patch(self, request, room_name):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            # get msg and update it
            msg = MessagesModel.objects.get(id=serializer.data["message_id"])

            emoji = serializer.data["emoji"]
            if emoji not in msg.reactions:
                msg.reactions[emoji] = {"count": 1, "users": [request.user.id]}
            else:
                if request.user.id not in msg.reactions[emoji]["users"]:
                    msg.reactions[emoji]["count"] += 1
                    msg.reactions[emoji]["users"].append(request.user.id)
                else:
                    return Response(
                        "you already reacted to this message",
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            msg.save()

            # send reaction to all users in room
            channel_layer = get_channel_layer()
            msg = ReactionSerializer(msg)

            try:
                async_to_sync(channel_layer.group_send)(
                    room_name,
                    {
                        "type": "send.messages",
                        "message_type": "reaction",
                        "data": msg.data,
                    },
                )

            except Exception as e:
                return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

            return Response(
                "reaction sent successfully", status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RemoveReactionMessage(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = SendReactionSerializer

    def patch(self, request, room_name):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            # get msg and update it
            msg = MessagesModel.objects.get(id=serializer.data["message_id"])

            emoji = serializer.data["emoji"]
            if emoji not in msg.reactions:
                return Response(
                    "reaction does not exist", status=status.HTTP_400_BAD_REQUEST
                )
            else:
                if request.user.id in msg.reactions[emoji]["users"]:
                    msg.reactions[emoji]["count"] -= 1
                    msg.reactions[emoji]["users"].remove(request.user.id)
                else:
                    return Response(
                        "this user did not react to this message",
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            msg.save()

            # send update to all users in room
            channel_layer = get_channel_layer()
            msg = ReactionSerializer(msg)

            try:
                async_to_sync(channel_layer.group_send)(
                    room_name,
                    {
                        "type": "send.messages",
                        "message_type": "reaction",
                        "data": msg.data,
                    },
                )

            except Exception as e:
                return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

            return Response(
                "reaction removed successfully", status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SendReport(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, message_id):
        try:
            msg = MessagesModel.objects.get(id=message_id)
            ReportModel.objects.create(reporter=request.user, reported_message=msg)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {"message": "report sent successfully"}, status=status.HTTP_201_CREATED
        )


class EditMessage(APIView):
    permission_classes = (IsAuthenticated,)

    def patch(self, request, message_id):
        pass


class DeleteMessage(APIView):
    permission_classes = (IsAuthenticated,)

    def delete(self, request, message_id):
        pass


class JoinChannel(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, room_name):
        try:
            room = ChannelsModel.objects.get(room_name=room_name)
        except ChannelsModel.DoesNotExist:
            return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)

        if request.user in room.users.all() or room.channel_type == "public":
            return Response(
                {"detail": "You already joined this channel"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        room.users.add(request.user.pk)

        return Response("Successfully joined", status=status.HTTP_200_OK)


class LeaveChannel(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, room_name):
        try:
            room = ChannelsModel.objects.get(room_name=room_name)
        except ChannelsModel.DoesNotExist:
            return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)

        if room.channel_type == "public":
            return Response(
                {"detail": "You cannot leave a public channel"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if request.user not in room.users.all():
            return Response(
                {"detail": "You are not in this channel"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        room.users.remove(request.user.pk)

        return Response("Successfully left channel", status=status.HTTP_200_OK)


class InvitePeopleToChannel(APIView):
    class InputSerializer(serializers.Serializer):
        email = serializers.EmailField()

    permission_classes = (IsAuthenticated,)
    serializer_class = InputSerializer

    def post(self, request, room_name):
        try:
            room = ChannelsModel.objects.get(room_name=room_name)
        except ChannelsModel.DoesNotExist:
            return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            email = serializer.data["email"]
            try:
                user = User.objects.get(email=email)
                if user in room.users.all():
                    return Response(
                        {"detail": "User already joined channel"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                else:
                    room.users.add(user.pk)
                    return Response(
                        "Successfully added user", status=status.HTTP_200_OK
                    )

            except User.DoesNotExist:
                send_email(
                    subject="Invite to Drop Me",
                    to=[email],
                    body=f"""User {request.user.username} invited you to join Drop Me community channel. Download the app now and join the recycling revolution!
                    """,
                )
                return Response(
                    "User not registered, Sent Email Invitaion",
                    status=status.HTTP_200_OK,
                )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
