from django.db import models
from users_api.models import UserModel


class MessagesModel(models.Model):
    user_model = models.ForeignKey(UserModel, related_name='user', on_delete=models.CASCADE)
    content = models.CharField(max_length=4000,null=True)
    message_dt = models.DateTimeField(auto_now_add=True)

    emoji=models.ManyToManyField(UserModel, related_name='blog_likes', blank=True)

    img = models.ImageField(upload_to='dropme_img_chat',null=True)
    video = models.FileField(upload_to='dropme_file_chat',null=True)
    # validators=[FileExtensionValidator(allowed_extensions=['MOV','avi','mp4','webm','mkv'])]

    def str(self):
        return self.user_model.username
    

class ChannelsModel(models.Model):
    room_name = models.CharField(max_length=50, default="welcome channels")
    participants=models.ManyToManyField(UserModel, related_name='chats')
    messages=models.ManyToManyField(MessagesModel, blank=True)

    @property
    def messages_num(self):
        """ return the number of messages inside specific channel"""
        if  self.messages and self.room_name:
            return self.messages.count()
        else :
            return 0