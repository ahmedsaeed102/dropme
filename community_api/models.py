import os
from django.db import models
from users_api.models import UserModel


class MessagesModel(models.Model):
    user_model = models.ForeignKey(UserModel, related_name='messages', on_delete=models.CASCADE)
    content = models.CharField(max_length=4000, null=True, blank=True)
    message_dt = models.DateTimeField(auto_now_add=True)

    # emoji=models.ManyToManyField(UserModel, related_name='blog_likes', blank=True)


    img = models.ImageField(upload_to='community/imgs', null=True, blank=True)
    video = models.FileField(upload_to='community/videos', null=True, blank=True)
    
    class Meta:
        ordering = ('-message_dt',)

    def str(self):
        return self.user_model.username
    

class ChannelsModel(models.Model):
    room_name = models.CharField(max_length=50)
    messages=models.ManyToManyField(MessagesModel, blank=True)

    # participants=models.ManyToManyField(UserModel, related_name='chats')

    @property
    def messages_num(self):
        """ return the number of messages inside specific channel"""
        if  self.messages and self.room_name:
            return self.messages.count()
        else :
            return 0
    
    @property
    def websocket_url(self):
        """ return the websocket url of specific channel"""
        if self.room_name:
            if os.environ.get('state') == 'production':
                return f'wss://dropme.up.railway.app/ws/chat/{self.room_name}/?token='
            else:
                return f'ws://localhost:8000/ws/chat/{self.room_name}/?token='
        else:
            return ''