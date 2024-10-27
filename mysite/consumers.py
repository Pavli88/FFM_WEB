import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from mysite.signals import notification_signal

class NotificationConsumer(AsyncWebsocketConsumer):
    print('WS CONNECT')
    async def connect(self):
        await self.accept()
        print('WS C')
        notification_signal.connect(self.send_notification)

    async def disconnect(self, close_code):
        print('WS DISCONNECT')
        notification_signal.disconnect(self.send_notification)

    async def send_notification(self, **kwargs):
        print('SEND NOTIFICATION')
        print(kwargs.get('message'))
        await self.send(text_data=json.dumps({
            'message': 'test'
        }))