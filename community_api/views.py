from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.generics import ListAPIView, RetrieveAPIView, CreateAPIView,DestroyAPIView, UpdateAPIView
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, NotFound
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from drf_spectacular.utils import extend_schema, OpenApiParameter
from django.shortcuts import get_object_or_404
from rest_framework import generics

from notification.services import notification_send_by_name, notification_send, fcmdevice_get
from users_api.services import email_send, user_list
from .models import ChannelsModel, MessagesModel, Invitations
from .services import community_get, Message, message_get, report_create
from .serializers import *

User = get_user_model()

def room(request, room_name):
    return render(request, "community_api/room.html", {"room_name": room_name})

class MessagesPagination(LimitOffsetPagination):
    default_limit = 5
    max_limit = 100

class ChannelsListView(ListAPIView):
    queryset = ChannelsModel.objects.all()
    serializer_class = ChannelsSerializer
    permission_classes = (IsAuthenticated,)

class ChannelsCreateView(CreateAPIView):
    queryset = ChannelsModel.objects.all()
    serializer_class = ChannelsCreateSerializer
    permission_classes = (IsAdminUser,)

    def perform_create(self, serializer):
        serializer.save()

class ChannelsDetailView(RetrieveAPIView):
    queryset = ChannelsModel.objects.all()
    serializer_class = ChannelsSerializer
    permission_classes = (IsAuthenticated,)

class ChannelsUpdateView(UpdateAPIView):
    queryset = ChannelsModel.objects.all()
    serializer_class = ChannelsSerializer
    permission_classes = (IsAdminUser,)

class ChannelsDeleteView(DestroyAPIView):
    queryset = ChannelsModel.objects.all()
    serializer_class = ChannelsSerializer
    permission_classes = (IsAdminUser,)

class JoinChannel(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, room_name):
        room = community_get(room_name=room_name)
        if request.user in room.users.all() or room.channel_type == "public":
            raise ValidationError({"detail": _("You already joined this channel")})
        room.users.add(request.user.pk)
        return Response("Successfully joined", status=status.HTTP_200_OK)

class LeaveChannel(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, room_name):
        room = community_get(room_name=room_name)
        if room.channel_type == "public":
            raise ValidationError({"detail": _("You cannot leave a public channel")})
        if request.user not in room.users.all():
            raise ValidationError({"detail": _("You are not in this channel")})
        room.users.remove(request.user.pk)
        return Response("Successfully left channel", status=status.HTTP_200_OK)

class AddPeopleToChannel(APIView):
    class AddInputSerializer(serializers.Serializer):
        emails = serializers.ListSerializer(child=serializers.EmailField())

    permission_classes = (IsAuthenticated,)
    serializer_class = AddInputSerializer

    def post(self, request, room_name):
        account = request.user
        room = community_get(room_name=room_name)
        if not (account in room.users.all() or room.channel_type == "public"):
            raise ValidationError({"detail": _("You are not in this channel")})
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        emails = serializer.validated_data["emails"]
        users = User.objects.filter(email__in=emails).exclude(user_channels__room_name=room_name)
        if not users:
            raise NotFound({"detail:": _("No users found")})
        notification_list = []
        for user in users:
            if not (user in room.users.all() or room.channel_type == "public"):
                room.users.add(user.pk)
                Invitations.objects.get_or_create(user=request.user, invited=user)
                notification_list.append(user)
        if not notification_list:
            raise ValidationError({"detail": _("Users already added")})
        devices = fcmdevice_get(user__in=notification_list)
        notification_send(
            devices=devices,
            users = notification_list,
            title="Community Invitation",
            body=f"user {request.user.username} added you in {room_name} channel",
            title_ar="دعوة إلى المجتمع",
            body_ar=f"قام المستخدم {request.user.username} بإضافتك إلى قناة {room.room_name_ar}"
        )
        return Response("Successfully added users")

class AlterNotificationRecieveView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, room_name):
        room = community_get(room_name=room_name)
        if request.user in room.notification_off_users.all():
            room.notification_off_users.remove(request.user)
            room.save()
            return Response("Successfully truned on notifications users")
        else:
            room.notification_off_users.add(request.user)
            room.save()
            return Response("Successfully truned off notifications users")

class SendEmailInvite(APIView):
    class EmailInputSerializer(serializers.Serializer):
        email = serializers.EmailField()

    permission_classes = (IsAuthenticated,)
    serializer_class = EmailInputSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        if User.objects.filter(email=email).exists():
            raise ValidationError({"detail": _("User already registered")})
        email_send(
            subject="Invite to Drop Me",
            to=[email],
            body=f"""User {request.user.username} invited you to join Drop Me community channel. Download the app now and join the recycling revolution!""",
        )
        return Response("user not registered, Sent Email Invitaion")

class UsersSearch(ListAPIView):
    class FilterSerializer(serializers.Serializer):
        email = serializers.EmailField()

    queryset = User.objects.all()
    serializer_class = UserInviteSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        filters_serializer = self.FilterSerializer(data=self.request.query_params)
        filters_serializer.is_valid(raise_exception=True)
        users = user_list(filters=filters_serializer.validated_data)
        return users

    def get_serializer_context(self):
        context = super(UsersSearch, self).get_serializer_context()
        room = community_get(room_name=self.room_name)
        context.update({"room": room})
        return context

    @extend_schema(parameters=[OpenApiParameter(name="email", location=OpenApiParameter.QUERY, description="User Email", required=True, type=str)])
    def get(self, request, room_name):
        self.room_name = room_name
        return super().get(request, room_name)

class PrevioulyInvited(ListAPIView):
    serializer_class = OutputSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        return Invitations.objects.filter(user=user)

    def get(self, request, room_name):
        self.room_name = room_name
        return super().get(request, room_name)

    def get_serializer_context(self):
        context = super(PrevioulyInvited, self).get_serializer_context()
        room = community_get(room_name=self.room_name)
        context.update({"room": room})
        return context

class ChannelMessages(ListAPIView):
    serializer_class = MessagesSerializer
    lookup_url_kwarg = "room_name"
    pagination_class = MessagesPagination

    def get_queryset(self):
        room_name = self.kwargs.get(self.lookup_url_kwarg)
        channel = community_get(room_name=room_name)
        self.channel_type = channel.channel_type
        self.room_name = channel.room_name
        self.room_name_ar = channel.room_name_ar
        self.description = channel.description
        self.description_ar = channel.description_ar
        messages = channel.messages.all()
        if not self.request.user.is_staff:
            messages = messages.filter(approved=True)
        return messages

    def get(self, request, *args, **kwargs):
        data = super().get(request, *args, **kwargs).data
        data["channel_type"] = self.channel_type
        data["room_name"] = self.room_name
        data["room_name_ar"] = self.room_name_ar
        data["description"] = self.description
        data["description_ar"] = self.description_ar
        return Response(data)

@extend_schema(request={"multipart/form-data": {"type": "object", "properties": {"content": {"type": "string", "format": "string"},"img": {"type": "string", "format": "binary"},"video": {"type": "string", "format": "binary"}, "gif": {"type": "string", "format": "binary"}, "file": {"type": "string", "format": "binary"}}}})
class SendMessage(APIView):
    serializer_class = SendMessageSerializer
    permission_classes = (IsAuthenticated,)
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, room_name):
        if not any(request.data.values()):
            raise ValidationError({"detail": _("message is empty")})
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        room = community_get(room_name=room_name)
        if room.is_admin_channel and not request.user.is_staff:
            raise ValidationError({"detail": _("Only admins can post in this channel")})
        Message.is_a_participant(room=room, user=request.user)
        new_message = Message.new_message_create(request=request, room=room, message_content=serializer.data["content"])
        if request.user.is_staff:
            new_message.approved = True
            new_message.save()
            Message.new_message_send(room_name=room_name, message=new_message, message_type="message")
            Message.new_message_notification_send(request=request, room_type=room.channel_type, room=room)
            return Response("message sent successfully", status=status.HTTP_201_CREATED)
        return Response("Message sent successfully, pending admin approval.", status=status.HTTP_201_CREATED)

class ApproveMessageView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, room_name, pk):
        room = community_get(room_name=room_name)
        message = get_object_or_404(MessagesModel, id=pk)
        if message.approved:
            raise ValidationError({"detail": _("Message already approved")})
        message.approved = True
        message.save()
        new_message = MessagesSerializer(message).data
        Message.new_message_send(room_name=room_name, message=new_message, message_type="message")
        Message.new_message_notification_send(request=request, room_type=room.channel_type, room=room)
        return Response({"detail": "Message approved successfully."}, status=status.HTTP_200_OK)

@extend_schema(methods=["PATCH"], exclude=True)
class EditMessage(UpdateAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = MessagesModel.objects.all()
    serializer_class = EditMessageSerializer

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

class SendReactionMessage(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = SendReactionSerializer

    def patch(self, request, room_name):
        room = community_get(room_name=room_name)
        Message.is_a_participant(room=room, user=request.user)
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        emoji = serializer.data["emoji"]
        message_id = serializer.data["message_id"]
        user_id = request.user.id
        message = message_get(message_id=message_id)
        message = Message.message_reaction_add(emoji=emoji, message=message, user_id=user_id)
        message = ReactionSerializer(message).data
        Message.new_message_send(room_name=room_name, message=message, message_type="reaction")
        notification_send_by_name(
            name=message.user_model.username,
            title=f"Reaction on your message",
            body=f"{request.user.username} reacted to your message.",
            title_ar = "رد على رسالتك",
            body_ar = f"{request.user.username} قام بالتفاعل مع رسالتك."
        )
        return Response("Reaction added successfully", status=status.HTTP_200_OK)

class ChangeReaction(APIView):
    class InputSerializer(serializers.Serializer):
        message_id = serializers.IntegerField()
        old_emoji = serializers.CharField(max_length=50)
        new_emoji = serializers.CharField(max_length=50)

    permission_classes = (IsAuthenticated,)
    serializer_class = InputSerializer

    def patch(self, request, room_name):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            old_emoji = serializer.data["old_emoji"]
            new_emoji = serializer.data["new_emoji"]
            message_id = serializer.data["message_id"]
            user_id = request.user.id
            message = message_get(message_id=message_id)
            message = Message.message_reaction_change(old_emoji=old_emoji, new_emoji=new_emoji, message=message, user_id=user_id)
            message = ReactionSerializer(message).data
            Message.new_message_send(room_name=room_name, message=message, message_type="reaction")
            return Response("Reaction changed successfully", status=status.HTTP_200_OK)
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
            message = message_get(message_id=message_id)
            Message.message_reaction_remove(emoji=emoji, message=message, user_id=user_id)
            message = ReactionSerializer(message).data
            Message.new_message_send(room_name=room_name, message=message, message_type="reaction")
            return Response("Reaction removed successfully", status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(request={"multipart/form-data": {"type": "object", "properties": {"content": {"type": "string", "format": "string"},"img": {"type": "string", "format": "binary"},"video": {"type": "string", "format": "binary"}}}})
class CommentListCreateView(generics.ListCreateAPIView):
    serializer_class = CommentsSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        message_id = self.kwargs['message_id']
        return CommentsModel.objects.filter(message_comment__id=message_id)

    def post(self, request, message_id):
        if not any(request.data.values()):
            raise ValidationError({"detail": _("comment is empty")})
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        message = MessagesModel.objects.get(id=message_id)
        serializer = serializer.save(user_model=self.request.user)
        message.comments.add(serializer)
        return Response("comment sent successfully", status=status.HTTP_201_CREATED)

class CommentUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CommentsSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return CommentsModel.objects.all()

class SendReport(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, message_id):
        report_create(request=request, message_id=message_id)
        return Response({"message": "Report sent successfully"}, status=status.HTTP_201_CREATED)