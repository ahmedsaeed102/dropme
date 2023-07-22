from django.urls import path
from .views import *


urlpatterns = [
    path("ws/chat/<str:room_name>/", room, name="room"),
    path("community/list/", ChannelsListView.as_view()),
    path("community/create/", ChannelsCreateView.as_view()),
    path("community/<pk>/", ChannelsDetailView.as_view()),
    path("community/<pk>/delete/", ChannelsDeleteView.as_view()),
    # path('community/<pk>/update/', ChannelsUpdateView.as_view()),
    # room messages
    path(
        "community/<str:room_name>/messages/",
        ChannelMessages.as_view(),
        name="room_messages",
    ),
    # report message
    path(
        "community/report/<int:message_id>/",
        SendReport.as_view(),
        name="report_message",
    ),
    # send message
    path(
        "community/<str:room_name>/send/",
        SendMessage.as_view(),
        name="send_message",
    ),
    # send reaction
    path(
        "community/<str:room_name>/send/reaction/",
        SendReactionMessage.as_view(),
        name="send_reaction",
    ),
    path(
        "community/<str:room_name>/remove/reaction/",
        RemoveReactionMessage.as_view(),
        name="Remove_reaction",
    ),
]
