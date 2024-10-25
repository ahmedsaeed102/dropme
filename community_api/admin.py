from django.contrib import admin
from .models import ChannelsModel, MessagesModel, ReportModel, Invitations, CommentsModel

admin.site.register(ChannelsModel)
admin.site.register(MessagesModel)
admin.site.register(ReportModel)
admin.site.register(Invitations)
admin.site.register(CommentsModel)
