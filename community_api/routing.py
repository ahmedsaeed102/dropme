from django.urls import path,include
# chat/routing.py
from django.urls import re_path

from . consumers import ChatConsumer

urlpatterns = [
    re_path(r"ws/chat/(?P<room_name>\w+)/$", ChatConsumer.as_asgi()),
    # re_path(r'^emoji/', include('emoji.urls')),
]