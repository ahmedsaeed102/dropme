import asyncio
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from .models import RecycleLog


class StartRecycle(AsyncJsonWebsocketConsumer):
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
            }
        )
        await asyncio.sleep(1)

        await self.send_json(
            {
                "status": "success",
                "message": "we are waiting for you to throw your bottle or can",
                "message_ar": "نحن في انتظارك لرمي الزجاجة أو العلبة",
            }
        )

    async def receive_json(self, content=None):
        print("recieve")

    async def disconnect(self, close_code):
        await database_sync_to_async(self.delete_incomplete_logs)()
        print("disconnected", close_code)

    def delete_incomplete_logs(self):
        RecycleLog.objects.filter(
            in_progess=True, channel_name=self.channel_name
        ).delete()

    def create_log(self):
        RecycleLog.objects.create(
            machine_name=self.machine_name,
            user=self.user,
            channel_name=self.channel_name,
            in_progess=True,
        )

    async def receive_update(self, event):
        await self.send_json(
            {
                "status": "success",
                "message": f"{event['bottles']} bottles and {event['cans']} cans",
                "message_ar": f"{event['bottles']} زجاجة و{event['cans']} علبة",
                "points": event["points"],
            }
        )
        # await update_user_points(self.user.pk, event['points'])
        # await database_sync_to_async(update_user_points)(self.user.pk, event["points"])
        await self.close()
