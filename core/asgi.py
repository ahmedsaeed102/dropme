import os
import django
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

django_asgi_app = get_asgi_application()

import machine_api.routing
import community_api.routing
from .channelsmiddleware import TokenAuthMiddleware


application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": TokenAuthMiddleware(
            URLRouter(
                machine_api.routing.urlpatterns + community_api.routing.urlpatterns
            ),
        ),
    }
)
