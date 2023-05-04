from django.urls import path
from .views import ChannelsListView, ChannelsDetailView, ChannelsCreateView, ChannelsDeleteView, index, room


app_name = 'community_api'

urlpatterns = [
    path("", index, name="index"),
    path("ws/chat/<str:room_name>/", room, name="room"),
    path('community/list/', ChannelsListView.as_view()),
    path('community/create/', ChannelsCreateView.as_view()),
    path('community/<pk>/', ChannelsDetailView.as_view()),
#     path('community/<pk>/update/', ChannelsUpdateView.as_view()),
    path('community/<pk>/delete/', ChannelsDeleteView.as_view())
]
