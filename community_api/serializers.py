from rest_framework import serializers
from django.core.validators import FileExtensionValidator
from users_api.models import UserModel
from .services import user_reaction_get
from .models import ChannelsModel, MessagesModel


class ChannelsSerializer(serializers.ModelSerializer):
    messages_num = serializers.SerializerMethodField()
    websocket_url = serializers.SerializerMethodField()
    joined = serializers.SerializerMethodField()

    class Meta:
        model = ChannelsModel
        exclude = ("messages", "users")
        read_only = "id"

    def get_messages_num(self, obj):
        return obj.messages_num

    def get_websocket_url(self, obj):
        return obj.websocket_url

    def get_joined(self, obj):
        request = self.context.get("request")

        return request.user in obj.users.all() or obj.channel_type == "public"


class ChannelsCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChannelsModel
        exclude = ("created_at", "messages", "users")


class MessagesSerializer(serializers.ModelSerializer):
    sender = serializers.SerializerMethodField()

    # room_name = serializers.SerializerMethodField()
    room = serializers.SerializerMethodField()
    # room_name_ar = serializers.SerializerMethodField()

    # description = serializers.SerializerMethodField()
    # description_ar = serializers.SerializerMethodField()

    sender_id = serializers.SerializerMethodField()
    sender_photo = serializers.SerializerMethodField()

    current_user_reaction = serializers.SerializerMethodField()

    class Meta:
        model = MessagesModel
        fields = (
            "id",
            "room",
            # "room_name_ar",
            # "description",
            # "description_ar",
            "sender_id",
            "sender",
            "sender_photo",
            "current_user_reaction",
            "content",
            "message_dt",
            "img",
            "video",
            "reactions",
        )

    # def get_room_name(self, obj):
    #     return obj.message_channel.get(messages__id=obj.id).room_name

    def get_room(self, obj):
        room = obj.message_channel.get(messages__id=obj.id)
        return {
            "room_name": room.room_name,
            "room_name_ar": room.room_name_ar,
            "description": room.description,
            "description_ar": room.description_ar,
        }

    # def get_room_name_ar(self, obj):
    #     return obj.message_channel.get(messages__id=obj.id).room_name_ar

    # def get_description(self, obj):
    #     return obj.message_channel.get(messages__id=obj.id).description

    # def get_description_ar(self, obj):
    #     return obj.message_channel.get(messages__id=obj.id).description_ar

    def get_sender(self, obj):
        return obj.user_model.username

    def get_sender_photo(self, obj):
        return obj.user_model.profile_photo.url

    def get_sender_id(self, obj):
        return obj.user_model.id

    def get_current_user_reaction(self, obj):
        request = self.context.get("request")
        if request:
            reaction = user_reaction_get(message=obj, user_id=request.user.id)
            return reaction

        return ""


class ReactionSerializer(serializers.ModelSerializer):
    msg_id = serializers.SerializerMethodField()

    class Meta:
        model = MessagesModel
        fields = ("msg_id", "reactions")

    def get_msg_id(self, obj):
        return obj.id


class SendReactionSerializer(serializers.Serializer):
    message_id = serializers.IntegerField()
    emoji = serializers.CharField(max_length=50)


class SendMessageSerializer(serializers.ModelSerializer):
    img = serializers.ImageField(
        required=False,
        validators=[
            FileExtensionValidator(allowed_extensions=["png", "jpeg", "jpg", "svg"]),
        ],
    )
    video = serializers.FileField(
        required=False,
        validators=[
            FileExtensionValidator(
                allowed_extensions=["MOV", "avi", "mp4", "webm", "mkv"]
            ),
        ],
    )

    class Meta:
        model = MessagesModel
        fields = ("content", "img", "video")


class UserInviteSerializer(serializers.ModelSerializer):
    joined = serializers.SerializerMethodField()

    class Meta:
        model = UserModel
        fields = ["id", "username", "email", "profile_photo", "joined"]

    def get_joined(self, obj):
        room = self.context["room"]
        if obj in room.users.all() or room.channel_type == "public":
            return True

        return False
