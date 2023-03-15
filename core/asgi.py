import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

import machine_api.routing
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from .channelsmiddleware import TokenAuthMiddleware

django_asgi_app  = get_asgi_application()

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": TokenAuthMiddleware(
        # AuthMiddlewareStack(URLRouter(machine_api.routing.websocket_urlpatterns))
       URLRouter(machine_api.routing.urlpatterns)
    ),
})