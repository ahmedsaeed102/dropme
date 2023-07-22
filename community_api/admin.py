from django.contrib import admin
from .models import ChannelsModel, MessagesModel, ReportModel


admin.site.register(ChannelsModel)
admin.site.register(MessagesModel)
admin.site.register(ReportModel)
