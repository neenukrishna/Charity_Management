import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import ChatMessage

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f"chat_{self.room_name}"
        print(f"[CONNECT] User {self.scope['user'].username} connecting to room: {self.room_group_name}")
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
    
    async def disconnect(self, close_code):
        print(f"[DISCONNECT] User {self.scope['user'].username} disconnecting from room: {self.room_group_name}")
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get('message')
        sender_username = data.get('sender')
        # Compute receiver from room name.
        id1, id2 = self.room_name.split('_')
        if str(self.scope["user"].id) == id1:
            receiver_id = id2
        else:
            receiver_id = id1
        
        sender = await database_sync_to_async(User.objects.get)(username=sender_username)
        receiver = await database_sync_to_async(User.objects.get)(id=receiver_id)
        chat_message = await self.save_message(sender, receiver, message)
        
        print(f"[RECEIVE] Message from {sender_username}: {message}")
        
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender': sender_username,
                'timestamp': chat_message.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            }
        )
    
    async def chat_message(self, event):
        print("[BROADCAST]", event)
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'sender': event['sender'],
            'timestamp': event['timestamp'],
        }))
    
    @database_sync_to_async
    def save_message(self, sender, receiver, message):
        return ChatMessage.objects.create(sender=sender, receiver=receiver, message=message)
