import asyncio
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from .models import RecycleLog, Machine
from users_api.models import UserModel


class StartRecycle(AsyncJsonWebsocketConsumer):

    def create_log(self):
        machine = Machine.objects.filter(identification_name=self.machine_name).first()
        if not machine:
            RecycleLog.objects.create(machine_name=self.machine_name, user=self.user, channel_name=self.channel_name, in_progess=True)
        else:
            RecycleLog.objects.create(machine_name=self.machine_name, user=self.user, channel_name=self.channel_name, in_progess=True, machine=machine)

    async def connect(self):
        try:
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
        except:
            await self.close()

    async def disconnect(self, close_code):
        bool = await database_sync_to_async(self.delete_incomplete_logs)()
        if not bool:
            points = await database_sync_to_async(self.get_user_points)()
            await self.send_json(
                {
                    "status": "success",
                    "points": points,
                })
        print("disconnected", close_code)

    def delete_incomplete_logs(self):
        recyclelog = RecycleLog.objects.filter(in_progess=True, channel_name=self.channel_name)
        if recyclelog:
            recyclelog.delete()
            return True
        return False

    def get_user_points(self):
        recyclelog = RecycleLog.objects.filter(channel_name=self.channel_name, is_complete=True).last()
        return recyclelog.points

    async def receive_update(self, event):
        print("pre received")
        if event.get("message"):
            print("received uodate", event)
            await self.send_json(
                {
                    "status": "error",
                    "message": event["message"],
                    "message_ar": event["message_ar"],
                })
        else:
            print("received finish", event)
            await self.send_json(
                {
                    "status": "success",
                    "message": f"{event['bottles']} bottles and {event['cans']} cans",
                    "message_ar": f"{event['bottles']} زجاجة و{event['cans']} علبة",
                    "points": event["points"],
                })
            await self.close()