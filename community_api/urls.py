from django.urls import path
from .views import *


urlpatterns = [
    path("ws/chat/<str:room_name>/", room, name="room"),
    path("community/list/", ChannelsListView.as_view()),
    path("community/create/", ChannelsCreateView.as_view()),
    path("community/<pk>/", ChannelsDetailView.as_view()),
    path("community/<pk>/delete/", ChannelsDeleteView.as_view()),
    # join, leave channel, turn off notification and add people
    path("community/<str:room_name>/join/", JoinChannel.as_view(), name="join_channel"),
    path("community/<str:room_name>/leave/", LeaveChannel.as_view(), name="leave_channel"),
    path("community/<str:room_name>/add/",AddPeopleToChannel.as_view(),name="invite_channel"),
    path('community/<str:room_name>/alter_recieve_notification/', AlterNotificationRecieveView.as_view(), name='add-notification-off-user'),
    # send email invitation
    path("users/email_invitation/",SendEmailInvite.as_view(),name="send_email_invitation"),
    # user search
    path("community/<str:room_name>/users/search/",UsersSearch.as_view(),name="user_search"),
    # previously invited
    path("community/<str:room_name>/previously_invited/",PrevioulyInvited.as_view()),
    # list, send, approve, update and delete messages
    path("community/<str:room_name>/messages/",ChannelMessages.as_view(),name="room_messages"),
    path("community/messages/<int:pk>/",MessageDetail.as_view(),name="message_detail"),
    path("community/<str:room_name>/send/",SendMessage.as_view(),name="send_message"),
    path('community/<str:room_name>/messages/<int:pk>/approve/', ApproveMessageView.as_view(), name='approve-message'),
    path("community/messages/<int:pk>/update/",EditMessage.as_view(),name="edit_message"),
    path("community/messages/<int:pk>/delete/",DeleteMessage.as_view(),name="delete_message"),
    # add, remove, change message reaction
    path("community/<str:room_name>/reaction/add/",SendReaction.as_view(),name="send_reaction"),
    path("community/<str:room_name>/reaction/remove/",RemoveReaction.as_view(),name="Remove_reaction"),
    path("community/<str:room_name>/reaction/change/",ChangeReaction.as_view(),name="change_reaction"),
    # list, add, remove, change comment
    path('community/messages/<int:message_id>/comments/', CommentListCreateView.as_view(), name='comment-list-create'),
    path('community/messages/comments/<int:pk>/', CommentUpdateDeleteView.as_view(), name='comment-update-delete'),
    # report message
    path("community/report/<int:message_id>/",SendReport.as_view(),name="report_message"),
]
