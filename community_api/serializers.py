from rest_framework import serializers
from django.core.validators import FileExtensionValidator

from users_api.models import UserModel
from .services import user_reaction_get
from .models import ChannelsModel, MessagesModel, Invitations, CommentsModel

class ChannelsSerializer(serializers.ModelSerializer):
    messages_num = serializers.SerializerMethodField()
    websocket_url = serializers.SerializerMethodField()
    joined = serializers.SerializerMethodField()
    recieve_notification = serializers.SerializerMethodField()

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

    def get_recieve_notification(self, obj):
        request = self.context.get("request")
        return False if request.user in obj.notification_off_users.all() else True

class ChannelsCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChannelsModel
        exclude = ("created_at", "messages", "users")

class UserInviteSerializer(serializers.ModelSerializer):
    joined = serializers.SerializerMethodField()

    def get_joined(self, obj):
        room = self.context["room"]
        if obj in room.users.all() or room.channel_type == "public":
            return True
        return False

    class Meta:
        model = UserModel
        fields = ["id", "username", "email", "profile_photo", "joined"]

class OutputSerializer(serializers.ModelSerializer):
        invited = UserInviteSerializer()
        class Meta:
            model = Invitations
            fields = ["invited"]

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.fields["invited"].context.update(self.context)

        def to_representation(self, obj):
            representation = super().to_representation(obj)
            invited_representation = representation.pop("invited")
            for key in invited_representation:
                representation[key] = invited_representation[key]
            return representation

class MessagesSerializer(serializers.ModelSerializer):
    sender = serializers.SerializerMethodField()
    sender_id = serializers.SerializerMethodField()
    sender_photo = serializers.SerializerMethodField()
    current_user_reaction = serializers.SerializerMethodField()
    comments_num = serializers.SerializerMethodField()

    class Meta:
        model = MessagesModel
        fields = ("id", "sender_id", "sender", "sender_photo", "current_user_reaction", "content", "message_dt", "img", "video", 'gif', 'file', "reactions", "approved", "comments_num")

    def get_sender(self, obj):
        return obj.user_model.username

    def get_sender_photo(self, obj):
        return obj.user_model.profile_photo.url

    def get_sender_id(self, obj):
        return obj.user_model.id

    def get_current_user_reaction(self, obj):
        request = self.context.get("request")
        if request:
            reaction = user_reaction_get(model=obj, user_id=request.user.id)
            return reaction
        return ""

    def get_comments_num(self, obj):
        return obj.comments_num

class SendMessageSerializer(serializers.ModelSerializer):
    img = serializers.ImageField(required=False,validators=[FileExtensionValidator(allowed_extensions=["png", "jpeg", "jpg", "svg"])])
    video = serializers.FileField(required=False,validators=[FileExtensionValidator(allowed_extensions=["MOV", "avi", "mp4", "webm", "mkv"])])
    gif = serializers.ImageField(required=False,validators=[FileExtensionValidator(allowed_extensions=["gif"])])
    file = serializers.FileField(required=False)

    class Meta:
        model = MessagesModel
        fields = ("content", "img", "video", "gif", "file")

class ReactionSerializer(serializers.ModelSerializer):
    msg_id = serializers.SerializerMethodField()

    class Meta:
        model = MessagesModel
        fields = ("msg_id", "reactions")

    def get_msg_id(self, obj):
        return obj.id

class CommentReactionSerializer(serializers.ModelSerializer):
    comment_id = serializers.SerializerMethodField()

    class Meta:
        model = CommentsModel
        fields = ("comment_id", "reactions")

    def get_comment_id(self, obj):
        return obj.id

class EditMessageSerializer(serializers.ModelSerializer):
        class Meta:
            model = MessagesModel
            fields = "__all__"

class SendReactionSerializer(serializers.Serializer):
    message_id = serializers.IntegerField()
    emoji = serializers.CharField(max_length=50)
    comment_id = serializers.IntegerField(required=False)

class CommentsSerializer(serializers.ModelSerializer):
    img = serializers.ImageField(required=False,validators=[FileExtensionValidator(allowed_extensions=["png", "jpeg", "jpg", "svg"])])
    video = serializers.FileField(required=False,validators=[FileExtensionValidator(allowed_extensions=["MOV", "avi", "mp4", "webm", "mkv"])])
    sender = serializers.SerializerMethodField()
    sender_id = serializers.SerializerMethodField()
    sender_photo = serializers.SerializerMethodField()
    current_user_reaction = serializers.SerializerMethodField()

    def get_sender(self, obj):
        return obj.user_model.username

    def get_sender_photo(self, obj):
        return obj.user_model.profile_photo.url

    def get_sender_id(self, obj):
        return obj.user_model.id

    def get_current_user_reaction(self, obj):
        request = self.context.get("request")
        if request:
            reaction = user_reaction_get(model=obj, user_id=request.user.id)
            return reaction
        return ""

    class Meta:
        model = CommentsModel
        fields = ['id', 'sender_id', 'sender', 'sender_photo', 'content', 'comment_dt', 'current_user_reaction', 'reactions', 'img', 'video']
        read_only_fields = ['user_model', 'comment_dt']