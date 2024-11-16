import asyncio
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from .models import RecycleLog
from .utlis import update_user_points, calculate_points


class StartRecycle(AsyncJsonWebsocketConsumer):
    def complete_logs(self):
        log = RecycleLog.objects.filter(in_progess=True, channel_name=self.channel_name)
        bottles = log.bottles
        cans = log.cans
        _, _, total_points = calculate_points(bottles, cans)
        log.points = total_points
        log.in_progess = False
        log.is_complete = True
        log.save()
        update_user_points(log.user.id, total_points)
        return bottles, cans, total_points

    def create_log(self):
        RecycleLog.objects.create(machine_name=self.machine_name, user=self.user, channel_name=self.channel_name, in_progess=True)

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
        bottles, cans, total_points = await database_sync_to_async(self.complete_logs)()
        await self.send_json(
            {
                "status": "success",
                "message": f"{bottles} bottles and {cans} cans",
                "message_ar": f"{bottles} زجاجة و{cans} علبة",
                "points": total_points,
            })

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
