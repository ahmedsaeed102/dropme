import asyncio
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from .models import RecycleLog
from .utlis import update_user_points


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
        
        await database_sync_to_async(self.create_log)()

        await self.send_json({
            'status': "success",
            'message': f'welcome {self.user.username}'
        })
        await asyncio.sleep(1)

        await self.send_json({
            'status': "success",
            'message': f'we are waiting for you to throw your bottle or can'
        })

        
    async def receive_json(self, content=None):
        print('recieve')

        
    async def disconnect(self, close_code):
        await database_sync_to_async(self.delete_incomplete_logs)()
        print('disconnected', close_code)

    
    def delete_incomplete_logs(self):
        RecycleLog.objects.filter(in_progess=True, channel_name=self.channel_name).delete()


    def create_log(self):
        RecycleLog.objects.create(
            machine_name=self.machine_name,
            user=self.user,
            channel_name=self.channel_name,
            in_progess=True
        )
    
    async def receive_update(self, event):
        print('here')
        await self.send_json({
            'status': "success",
            'message': f"{event['bottles']} bottles and {event['cans']} cans",
            'points': event['points']
        })
        await update_user_points(self.user.pk, event['points'])
        await self.close()
