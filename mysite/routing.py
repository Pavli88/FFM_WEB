from django.urls import re_path
from . import consumers

ws_url = [
    re_path("connection/", consumers.CoreConsumer.as_asgi()),
]
