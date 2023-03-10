# from django.db import models

# # Create your models here.
# from django.db import models
# from users_api.models import UserModel
# #  from emoji_picker.widgets import EmojiPickerTextInputAdmin
# from django.apps import apps
# # # # Create your models here.


# class ChannelsModel(models.Model):
#     channel_name = models.CharField(max_length=50)
#     # posts_num = PostsModel.get_posts_num(PostsModel)

#     def str(self):
#         return self.channel_name


# class PostsModel(models.Model):

#     user_model = models.ForeignKey(UserModel, related_name='user', on_delete=models.CASCADE)
#     channel_model = models.ForeignKey(ChannelsModel, related_name='channel', on_delete=models.CASCADE)
#     message = models.CharField(max_length=4000)
#     message_dt = models.DateTimeField(auto_now_add=True)
#     #  emoji = models.CharField(widget=EmojiPickerTextInputAdmin)

#     def str(self):

#         return self.channel_model

#     def get_posts_num(self):
#         return self.objects.all().count()

