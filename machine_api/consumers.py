import asyncio
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from .models import RecycleLog


class StartRecycle(AsyncJsonWebsocketConsumer):
    def delete_incomplete_logs(self):
        RecycleLog.objects.filter(in_progess=True, channel_name=self.channel_name).delete()

    def create_log(self):
        RecycleLog.objects.create(machine_name=self.machine_name, user=self.user, channel_name=self.channel_name, in_progess=True)

    async def connect(self):
        await self.accept()
        self.user = self.scope["user"]
        self.machine_name = self.scope["url_route"]["kwargs"]["name"]
        await database_sync_to_async(self.create_log)()
        await self.send_json(
            {
                "status": "success",
                "message": f"welcome {self.user.username}",
                "message_ar": f"مرحبا {self.user.username}",
            })
        await asyncio.sleep(1)
        await self.send_json(
            {
                "status": "success",
                "message": "we are waiting for you to throw your bottle or can",
                "message_ar": "نحن في انتظارك لرمي الزجاجة أو العلبة",
            })
        await asyncio.sleep(1)

    async def receive_update(self, event):
        await self.send_json({
            "status": "success",
            "message": f"you have thrown {event['bottles']} bottles and {event['cans']} cans",
            "message_ar": f"لقد قمت برمي {event['bottles']} زجاجة و {event['cans']} علبة",
        })
        print("received", event)

    async def disconnect(self, close_code):
        await database_sync_to_async(self.delete_incomplete_logs)()
        print("disconnected", close_code)

    async def receive_finish(self, event):
        await self.send_json(
            {
                "status": "success",
                "message": f"{event['bottles']} bottles and {event['cans']} cans",
                "message_ar": f"{event['bottles']} زجاجة و{event['cans']} علبة",
                "points": event["points"],
            })
        print("received finish", event)
        await self.close()
