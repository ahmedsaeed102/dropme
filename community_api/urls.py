from django.urls import path
from .views import *


urlpatterns = [
    path("ws/chat/<str:room_name>/", room, name="room"),
    path("community/list/", ChannelsListView.as_view()),
    path("community/create/", ChannelsCreateView.as_view()),
    path("community/<pk>/", ChannelsDetailView.as_view()),
    path("community/<pk>/delete/", ChannelsDeleteView.as_view()),
    # path('community/<pk>/update/', ChannelsUpdateView.as_view()),
    # join, leave channel and add people
    path("community/<str:room_name>/join/", JoinChannel.as_view(), name="join_channel"),
    path(
        "community/<str:room_name>/leave/", LeaveChannel.as_view(), name="leave_channel"
    ),
    path(
        "community/<str:room_name>/add/",
        InvitePeopleToChannel.as_view(),
        name="invite_channel",
    ),
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
    # update & delete message
    path(
        "community/messages/<int:pk>/update/",
        EditMessage.as_view(),
        name="edit_message",
    ),
    path(
        "community/messages/<int:pk>/delete/",
        DeleteMessage.as_view(),
        name="delete_message",
    ),
    # send reaction
    path(
        "community/<str:room_name>/reaction/add/",
        SendReactionMessage.as_view(),
        name="send_reaction",
    ),
    path(
        "community/<str:room_name>/reaction/remove/",
        RemoveReactionMessage.as_view(),
        name="Remove_reaction",
    ),
    path(
        "community/<str:room_name>/reaction/change/",
        ChangeReaction.as_view(),
        name="change_reaction",
    ),
]
