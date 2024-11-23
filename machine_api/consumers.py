# import asyncio
# from channels.generic.websocket import AsyncJsonWebsocketConsumer
# from channels.db import database_sync_to_async
# from .models import RecycleLog
# from .utlis import update_user_points, calculate_points


# class StartRecycle(AsyncJsonWebsocketConsumer):

#     def create_log(self):
#         RecycleLog.objects.create(machine_name=self.machine_name, user=self.user, channel_name=self.channel_name, in_progess=True)

#     async def connect(self):
#         try:
#             await self.accept()
#             self.user = self.scope["user"]
#             self.machine_name = self.scope["url_route"]["kwargs"]["name"]
#             await database_sync_to_async(self.create_log)()
#             await self.send_json(
#                 {
#                     "status": "success",
#                     "message": f"welcome {self.user.username}",
#                     "message_ar": f"مرحبا {self.user.username}",
#                 })
#             await asyncio.sleep(1)
#             await self.send_json(
#                 {
#                     "status": "success",
#                     "message": "we are waiting for you to throw your bottle or can",
#                     "message_ar": "نحن في انتظارك لرمي الزجاجة أو العلبة",
#                 })
#         except:
#             await self.close()

#     async def disconnect(self, close_code):
#         await database_sync_to_async(self.delete_incomplete_logs)()
#         print("disconnected", close_code)

#     def delete_incomplete_logs(self):
#         RecycleLog.objects.filter(
#             in_progess=True, channel_name=self.channel_name
#         ).delete()

#     async def receive_update(self, event):
#         print("pre received")
#         if event.get("message"):
#             print("received uodate", event)
#             await self.send_json(
#                 {
#                     "status": "error",
#                     "message": event["message"],
#                     "message_ar": event["message_ar"],
#                 })
#         else:
#             print("received finish", event)
#             await self.send_json(
#                 {
#                     "status": "success",
#                     "message": f"{event['bottles']} bottles and {event['cans']} cans",
#                     "message_ar": f"{event['bottles']} زجاجة و{event['cans']} علبة",
#                     "points": event["points"],
#                 })
#             await self.close()

import asyncio
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from .models import RecycleLog
from .utlis import update_user_points, calculate_points


class StartRecycle(AsyncJsonWebsocketConsumer):
    async def connect(self):
        try:
            await self.accept()
            self.user = self.scope["user"]
            self.machine_name = self.scope["url_route"]["kwargs"]["name"]
            self.group_name = f"machine_{self.machine_name}"
            await self.channel_layer.group_add(self.group_name, self.channel_name)

            await database_sync_to_async(self.create_log)()
            await self.send_json(
                {
                    "status": "success",
                    "message": f"Welcome {self.user.username}",
                    "message_ar": f"مرحبا {self.user.username}",
                }
            )
            await asyncio.sleep(1)
            await self.send_json(
                {
                    "status": "success",
                    "message": "We are waiting for you to throw your bottle or can",
                    "message_ar": "نحن في انتظارك لرمي الزجاجة أو العلبة",
                }
            )
        except Exception as e:
            print(f"Error in connect: {e}")
            await self.close()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
        await database_sync_to_async(self.delete_incomplete_logs)()
        print(f"Disconnected {self.channel_name}, code: {close_code}")

    def create_log(self):
        RecycleLog.objects.create(
            machine_name=self.machine_name,
            user=self.user,
            channel_name=self.channel_name,
            in_progess=True,
        )

    def delete_incomplete_logs(self):
        RecycleLog.objects.filter(in_progess=True, channel_name=self.channel_name).delete()

    async def receive_update(self, event):
        print("pre received")
        if event.get("message"):
            print("received update", event)
            await self.send_json(
                {
                    "status": "error",
                    "message": event["message"],
                    "message_ar": event["message_ar"],
                }
            )
        else:
            print("received finish", event)
            await self.send_json(
                {
                    "status": "success",
                    "message": f"{event['bottles']} bottles and {event['cans']} cans",
                    "message_ar": f"{event['bottles']} زجاجة و{event['cans']} علبة",
                    "points": event["points"],
                }
            )
            await self.close()
