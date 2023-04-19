from django.shortcuts import render

# chat/views.py
from django.shortcuts import render


def index(request):
    return render(request, "community_api/index.html")

def room(request, room_name):
    return render(request, "community_api/room.html", {"room_name": room_name})