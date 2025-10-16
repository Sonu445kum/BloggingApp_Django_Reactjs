"""
ASGI config for blog_project project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application
import blog.routing  # Make sure you create this file for websocket URLs

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'blog_project.settings')

# Django ASGI application for HTTP requests
django_asgi_app = get_asgi_application()

# Main ASGI application with WebSocket support
application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter(
            blog.routing.websocket_urlpatterns
        )
    ),
})
