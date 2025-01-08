from django.urls import path, re_path
from .consumer import ChatConsumer

wsPattern = [re_path(r'ws/chat/(?P<room_name>\w+)/$', ChatConsumer.as_asgi()),]