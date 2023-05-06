from django.urls import path
from .views import (
    ChannelsListView, 
    ChannelsDetailView, 
    ChannelsCreateView, 
    ChannelsDeleteView,
    ChannelMessages,
    ImgUpload,
    VideoUpload,
    # FileUpload,
    room
)


app_name = 'community_api'

urlpatterns = [
    path("ws/chat/<str:room_name>/", room, name="room"),
    path('community/list/', ChannelsListView.as_view()),
    path('community/create/', ChannelsCreateView.as_view()),
    path('community/<pk>/', ChannelsDetailView.as_view()),
    path('community/<str:room_name>/messages/', ChannelMessages.as_view(), name='room_messages'),
    path("community/<str:room_name>/upload/img/", ImgUpload.as_view(), name="upload_img"),
    path("community/<str:room_name>/upload/video/", VideoUpload.as_view(), name="upload_video"),
    # path("community/<str:room_name>/upload/file/", FileUpload.as_view(), name="upload_file"),
#     path('community/<pk>/update/', ChannelsUpdateView.as_view()),
    path('community/<pk>/delete/', ChannelsDeleteView.as_view())
]
