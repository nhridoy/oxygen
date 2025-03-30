from django.urls import re_path

from .consumers import AsyncWebConsumer

websocket_urlpatterns = [
    re_path(r"^ws/connect/(?P<key>[\w-]*)/$", AsyncWebConsumer.as_asgi()),
]
