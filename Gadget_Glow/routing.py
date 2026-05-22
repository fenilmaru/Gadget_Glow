from django.urls import re_path
from channels.routing import URLRouter
from channels.auth import AuthMiddlewareStack
from orders.consumers import OrderConsumer
from notifications.consumers import NotificationConsumer

websocket_urlpatterns = [
    re_path(r'ws/orders/(?P<order_id>\d+)/$', OrderConsumer.as_asgi()),
    re_path(r'ws/notifications/$', NotificationConsumer.as_asgi()),
]
