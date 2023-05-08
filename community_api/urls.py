from django.urls import path
from .views import *


urlpatterns = [
    path("ws/chat/<str:room_name>/", room, name="room"),
    path('community/list/', ChannelsListView.as_view()),
    path('community/create/', ChannelsCreateView.as_view()),
    path('community/<pk>/', ChannelsDetailView.as_view()),
    path('community/<pk>/delete/', ChannelsDeleteView.as_view()),
    # path('community/<pk>/update/', ChannelsUpdateView.as_view()),

    path('community/<str:room_name>/messages/', ChannelMessages.as_view(), name='room_messages'),
    
    path("community/<str:room_name>/send/text/", SendTextMessage.as_view(), name="send_text"),

    path("community/<str:room_name>/send/reaction/", SendReactionMessage.as_view(), name="send_reaction"),
    path("community/<str:room_name>/remove/reaction/", RemoveReactionMessage.as_view(), name="Remove_reaction"),

    path("community/<str:room_name>/send/img/", SendImgMessage.as_view(), name="send_img"),
    path("community/<str:room_name>/send/video/", SendVideoMessage.as_view(), name="send_video"),
]