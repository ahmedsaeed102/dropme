from django.urls import path
from .views import Notifications, ReadNotifications, DeleteNotifications

urlpatterns = [
    path('notifications/', Notifications.as_view(http_method_names=['get']), name='notifications-list'),
    path('notifications/read/', ReadNotifications.as_view(http_method_names=['post']), name='read-notifications'),
    path('notifications/delete/', DeleteNotifications.as_view(http_method_names=['post']), name='delete-notifications'),
]
