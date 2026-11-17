from django.urls import path

from apps.realtime.consumers import BoardConsumer

websocket_urlpatterns = [
    path("ws/board/", BoardConsumer.as_asgi()),
]