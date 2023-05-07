from channels.generic.websocket import AsyncJsonWebsocketConsumer


class ChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]

        # Join room group
        await self.channel_layer.group_add(self.room_name, self.channel_name)

        await self.accept()

    
    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_name, self.channel_name)
        print('disconnected', close_code)


    # Receive message from WebSocket
    async def receive_json(self, data):
        print(data)
    

    async def send_messages(self, data):
        # Send message to all users in the room
        await self.send_json(data)