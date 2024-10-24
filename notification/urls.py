from django.urls import path
from .views import Notifications

urlpatterns = [
    path('notifications/', Notifications.as_view(http_method_names=['get']), name='notifications-list'),
    path('notifications/<int:pk>/', Notifications.as_view(http_method_names=['get', 'delete', 'patch']), name='notification-detail'),
]
