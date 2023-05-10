from rest_framework import serializers
from users_api.serializers import UserSerializer
from .models import ChannelsModel, MessagesModel


class ChannelsSerializer(serializers.ModelSerializer):
    # participants = MessageSerializer(many=True)
    messages_num = serializers.SerializerMethodField()
    websocket_url = serializers.SerializerMethodField()

    class Meta:
        model = ChannelsModel
        exclude=("messages",)
        read_only = ('id')
    
    def get_messages_num(self, obj):
        return obj.messages_num
    
    def get_websocket_url(self, obj):
        return obj.websocket_url


class ChannelsCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChannelsModel
        fields = ('room_name',)


class MessagesSerializer(serializers.ModelSerializer):
    sender=serializers.SerializerMethodField()
    sender_photo = serializers.SerializerMethodField()
    class Meta:
        model = MessagesModel
        fields = ('id', 'sender', 'sender_photo', 'content', 'message_dt', 'img', 'video', 'reactions')
    
    def get_sender(self,obj):
        return obj.user_model.username
    
    def get_sender_photo(self,obj):
        return obj.user_model.profile_photo.url


class ReactionSerializer(serializers.ModelSerializer):
    msg_id = serializers.SerializerMethodField()

    class Meta:
        model = MessagesModel
        fields = ('msg_id', "reactions")

    def get_msg_id(self, obj):
        return obj.id


class SendReactionSerializer(serializers.Serializer):
    message_id = serializers.IntegerField()
    emoji = serializers.CharField(max_length=50)


class TextMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessagesModel
        fields = ('content',)


class ImgUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessagesModel
        fields = ('img',)


class VideoUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessagesModel
        fields = ('video',)