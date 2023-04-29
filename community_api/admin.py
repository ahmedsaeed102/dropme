from django.contrib import admin
from .models import ChannelsModel, MessagesModel


admin.site.register(ChannelsModel)
admin.site.register(MessagesModel)