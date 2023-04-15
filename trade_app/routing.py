from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path('price_stream/', consumers.PriceStream.as_asgi()),
]