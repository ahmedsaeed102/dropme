from django.urls import path
from .views import *

urlpatterns = [
    path("notifications/", Notifications.as_view(), name="notifications"),
    path(
        "notifications/<int:pk>/",
        DeleteNotification.as_view(),
        name="delete_notifications",
    ),
]
