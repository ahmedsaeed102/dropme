import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
# from channels.auth import AuthMiddlewareStack
# from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application
from .channelsmiddleware import TokenAuthMiddleware

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

django_asgi_app  = get_asgi_application()

import machine_api.routing

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": TokenAuthMiddleware(
        # AuthMiddlewareStack(URLRouter(machine_api.routing.websocket_urlpatterns))
       URLRouter(machine_api.routing.urlpatterns)
    ),
})