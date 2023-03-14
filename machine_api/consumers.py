import asyncio
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async

class StartRecycle(AsyncJsonWebsocketConsumer):
    '''
    this class should open a socket connection between server and mobile app until recycling is done
    it should also claculate the points and add it to user total points, and if
    there is an ongoing competion, it should add it to user competition points
    '''   
    async def connect(self):
        await self.accept()

        self.user = self.scope["user"]
        self.machine_name = self.scope['url_route']['kwargs']['name']

        # self.username = await database_sync_to_async(self.get_name)()
        await self.send_json({
            'username': self.user.username,
            'machine_name': self.machine_name
        })
        await self.close()

        # self.websocket_disconnect('disconnect')
        # while self.connected:
        #     await asyncio.sleep(5)
        #     await self.send({
        #     'type': 'websocket.send',
        #     'text': "hi"
        # })
        
    async def receive_json(self, content=None):
        print('recieve')
        # await self.send({
        #     'type': 'websocket.send',
        #     'payload': event['text']
        # })
        
    async def disconnect(self, close_code):
        print('disconnected')
    
    def get_name(self):
        pass

