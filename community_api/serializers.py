from rest_framework import serializers
from .models import ChannelsModel, MessagesModel
from users_api.serializers import UserSerializer

# ===============================async part=====================================
# class MessageSerializer(serializers.StringRelatedField):
#     def to_internal_value(self, value):
#         return value
    

class MessagecontentSerializer(serializers.ModelSerializer):
    emoji = UserSerializer(many=True, read_only=True)
    user_model = serializers.SerializerMethodField()
    emoji_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model=MessagesModel
        fields=('id', 'user_model', 'content','message_dt','emoji','emoji_count','is_liked')
    def get_sender(self,obj):
        return obj.user_model.username
    def get_emoji_count(self,obj):
        return len(obj.emoji.all())
    def get_is_liked(self,obj):
        user=self.context['request'].user
        return True if user in obj.emoji.all() else False


class MessageImgSerializer(serializers.ModelSerializer):
    emoji=UserSerializer(many=True,read_only=True)
    user_model=serializers.SerializerMethodField()
    emoji_count=serializers.SerializerMethodField()
    is_liked=serializers.SerializerMethodField()
    class Meta:
        model=MessagesModel
        fields=('id', 'user_model', 'content','message_dt','img','emoji_count','is_liked')
    def get_sender(self,obj):
        return obj.user_model.username
    def get_emoji_count(self,obj):
        return len(obj.emoji.all())
    def get_is_liked(self,obj):
        user=self.context['request'].user
        return True if user in obj.emoji.all() else False


class MessageVideoSerializer(serializers.ModelSerializer):
    emoji=UserSerializer(many=True,read_only=True)
    user_model=serializers.SerializerMethodField()
    emoji_count=serializers.SerializerMethodField()
    is_liked=serializers.SerializerMethodField()
    class Meta:
        model=MessagesModel
        fields=('id', 'user_model', 'content','message_dt','video','emoji_count','is_liked')
    def get_sender(self,obj):
        return obj.user_model.username
    def get_emoji_count(self,obj):
        return len(obj.emoji.all())
    def get_is_liked(self,obj):
        user=self.context['request'].user
        return True if user in obj.emoji.all() else False


# =========================================sync==================================
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
        fields = ('id', 'sender','sender_photo', 'content', 'message_dt', 'img', 'video')
    
    def get_sender(self,obj):
        return obj.user_model.username
    
    def get_sender_photo(self,obj):
        return obj.user_model.profile_photo.url


# validators=[FileExtensionValidator(allowed_extensions=['MOV','avi','mp4','webm','mkv'])]