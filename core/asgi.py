import os


from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator

import django

from django.core.asgi import get_asgi_application

from community_api.routing import websocket_urlpatterns
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

django_asgi_app  = get_asgi_application()

import machine_api.routing
# from .channelsmiddleware import TokenAuthMiddleware
import community_api.routing


application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": AllowedHostsOriginValidator(
            AuthMiddlewareStack(URLRouter(websocket_urlpatterns),URLRouter(machine_api.routing.urlpatterns))
            
    ),
        ),
    }
)

