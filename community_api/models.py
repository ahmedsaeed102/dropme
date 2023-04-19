

from django.db import models
from users_api.models import UserModel
# from emoji_picker.widgets import EmojiPickerTextInputAdmin




class ChannelsModel(models.Model):
    channel_name = models.CharField(max_length=50,default="welcome channels")

    def str(self):
        return self.channel_name
    
    

class MessagesModel(models.Model):

    user_model = models.ForeignKey(UserModel, related_name='user', on_delete=models.CASCADE)
    channel_id = models.ForeignKey(ChannelsModel, related_name='channel', on_delete=models.CASCADE)
    message = models.CharField(max_length=4000)
    message_dt = models.DateTimeField(auto_now_add=True)
    emoji=models.ManyToManyField(UserModel, related_name='blog_likes', blank=True)
    img = models.ImageField(upload_to='dropme_img_chat',null=True)
    video = models.FileField(upload_to='dropme_file_chat',null=True)
    # ,
# validators=[FileExtensionValidator(allowed_extensions=['MOV','avi','mp4','webm','mkv'])]

    
   
    def str(self):
        return self.user_model.username
    
    @property
    def get_messages_num(self):
        """ return the number of messages inside specific channel"""
        return MessagesModel.objects.filter(channel_id=self.channel_id).count()
    
    def last_10_messages(self):
        """ return the last recent 10 messages """
        return self.objects.order_by('-message_dt').all()[:10]
