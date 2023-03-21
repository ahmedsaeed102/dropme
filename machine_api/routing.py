from django.urls import path

from . import consumers

urlpatterns = [
    path("machines/recycle/start/<str:name>/", consumers.StartRecycle.as_asgi(), name='start_recycle'),
]