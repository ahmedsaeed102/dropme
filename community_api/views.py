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
)
from users_api.services import email_send
from .models import ChannelsModel, MessagesModel, ReportModel
from .services import community_get, NewMessage, message_get
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
    permission_classes = (IsAdminUser,)


class ChannelsDeleteView(DestroyAPIView):
    queryset = ChannelsModel.objects.all()
    serializer_class = ChannelsSerializer
    permission_classes = (IsAdminUser,)


class ChannelMessages(ListAPIView):
    serializer_class = MessagesSerializer
    lookup_url_kwarg = "room_name"
    pagination_class = MessagesPagination

    def get_queryset(self):
        room_name = self.kwargs.get(self.lookup_url_kwarg)
        channel = community_get(room_name=room_name)
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
        if not request.data:
            return Response("message is empty", status=status.HTTP_400_BAD_REQUEST)

        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            room = community_get(room_name=room_name)
            if room.channel_type == "private" and request.user not in room.users.all():
                return Response(
                    "you are not in this room to send messages",
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # create new msg
            new_message = NewMessage.new_message_create(
                request=request, room=room, message_content=serializer.data["content"]
            )

            # send msg to all users in room
            new_message = MessagesSerializer(new_message).data
            try:
                NewMessage.new_message_send(
                    room_name=room_name, message=new_message, message_type="message"
                )
            except Exception as e:
                return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

            # send notification
            NewMessage.new_message_notification_send(
                request=request, room_type=room.channel_type, room_name=room_name
            )

            return Response("message sent successfully", status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SendReactionMessage(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = SendReactionSerializer

    def patch(self, request, room_name):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            emoji = serializer.data["emoji"]
            message_id = serializer.data["message_id"]
            user_id = request.user.id

            # get msg and update it
            msg = message_get(message_id=message_id)

            if emoji not in msg.reactions:
                return Response("emoji not found", status=status.HTTP_400_BAD_REQUEST)
            else:
                if user_id not in msg.reactions[emoji]["users_ids"]:
                    msg.reactions[emoji]["count"] += 1
                    msg.reactions[emoji]["users_ids"].append(user_id)
                    msg.reactions[emoji]["users"].append(
                        {"id": user_id, "reaction": emoji}
                    )
                    msg.save()
                else:
                    return Response(
                        "You already reacted to this message",
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            # send reaction to all users in room
            msg = ReactionSerializer(msg).data
            try:
                NewMessage.new_message_send(
                    room_name=room_name, message=msg, message_type="reaction"
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
            emoji = serializer.data["emoji"]
            message_id = serializer.data["message_id"]
            user_id = request.user.id

            # get msg and update it
            msg = message_get(message_id=message_id)

            if emoji not in msg.reactions:
                return Response(
                    "reaction does not exist", status=status.HTTP_400_BAD_REQUEST
                )
            else:
                if user_id in msg.reactions[emoji]["users_ids"]:
                    msg.reactions[emoji]["count"] -= 1
                    msg.reactions[emoji]["users_ids"].remove(user_id)
                    msg.reactions[emoji]["users"] = [
                        dictionary
                        for dictionary in msg.reactions[emoji]["users"]
                        if dictionary.get("id") != user_id
                    ]
                    msg.save()
                else:
                    return Response(
                        "this user did not react to this message",
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            # send update to all users in room
            msg = ReactionSerializer(msg).data
            try:
                NewMessage.new_message_send(
                    room_name=room_name, message=msg, message_type="reaction"
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


@extend_schema(methods=["PATCH"], exclude=True)
class EditMessage(UpdateAPIView):
    class EditSerializer(serializers.ModelSerializer):
        class Meta:
            model = MessagesModel
            fields = ["content"]

    permission_classes = (IsAuthenticated,)
    queryset = MessagesModel.objects.all()
    serializer_class = EditSerializer

    def put(self, request, *args, **kwargs):
        instance = self.get_object()
        if not instance.user_model == request.user or not instance.content:
            return Response(status=status.HTTP_403_FORBIDDEN)

        return self.update(request, *args, **kwargs)


class DeleteMessage(DestroyAPIView):
    queryset = MessagesModel.objects.all()
    serializer_class = MessagesSerializer
    permission_classes = (IsAuthenticated,)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if not instance.user_model == request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)

        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class JoinChannel(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, room_name):
        room = community_get(room_name=room_name)

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
        room = community_get(room_name=room_name)

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
        room = community_get(room_name=room_name)

        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            email = serializer.data["email"]
            try:
                user = User.objects.get(email=email)
                if user in room.users.all() or room.channel_type == "public":
                    return Response(
                        {"detail": "User already joined channel"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                else:
                    room.users.add(user.pk)

                    # send notification
                    device = fcmdevice_get(user=user)
                    notification_send(
                        devices=device,
                        title="Community Invitation",
                        body=f"user {request.user.username} added you in {room_name} channel",
                    )

                    return Response(
                        "Successfully added user", status=status.HTTP_200_OK
                    )

            except User.DoesNotExist:
                email_send(
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
