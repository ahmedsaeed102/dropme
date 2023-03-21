from django.urls import path

from .consumers import ChatConsumer


websocket_urlpatterns = [
    path("/community/<str:room_name>", ChatConsumer.as_asgi()),
]