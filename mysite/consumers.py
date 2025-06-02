import json
from channels.generic.websocket import AsyncWebsocketConsumer

class CoreConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        await self.channel_layer.group_add(f"user_{self.user.id}", self.channel_name)
        await self.accept()

    async def receive(self, text_data):
        data = json.loads(text_data)
        event_type = data.get("type")
        payload = data.get("payload")

        if event_type == "chat.message":
            await self.handle_chat(payload)
        elif event_type == "notification.read":
            await self.mark_notification_as_read(payload)
        # stb.

    async def process_completed(self, event):
        await self.send(text_data=json.dumps({
            "type": "process.completed",
            "payload": event["payload"]
        }))

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            "type": "chat.message",
            "payload": event["payload"]
        }))