from asgiref.sync import async_to_sync
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from community_api.models import MessagesModel
from users_api.models import UserModel
from .utlis import get_current_chat


class ChatConsumer(AsyncJsonWebsocketConsumer):
    # def get_command(self, command):
    #     """ to filter the specific operation when we used receive method"""
    #     # our chat commands
    #     commands={
    #         'add_messages':self.add_newmessages,
    #         # 'fetch_messages':fetch_10recent_messages,
    #         # 'add_files':add_newfiles,
    #         # 'add_newemojis':add_newemojis,
    #         # 'add_imgs':add_newimgs
    #     }
    #     return commands[command]

    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"

        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()

    
    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        print('disconnected', close_code)


    # Receive message from WebSocket
    async def receive_json(self, data):
        # used to handle logic of every command 
        # command = self.get_command(data['command'])
        # await command(data)
        print(data)
        
        message = await self.create_message(data)

        await self.channel_layer.group_send(self.room_group_name, 
        {'type':'send.messages', 
         'message':data['message'],
         'time': str(message.message_dt),
         'sender':self.scope["user"].username,
         "sender_image":self.scope["user"].profile_photo.url
        })
    

    async def send_messages(self, data):
        # Send message to all users in the room
        await self.send_json(data)


    @database_sync_to_async
    def create_message(self, data):
        author=self.scope["user"]

        message=MessagesModel.objects.create(user_model=author, 
        content=data.get('message', ""))

        current_chat=get_current_chat(self.room_name)
        current_chat.messages.add(message)
        current_chat.save()

        return message


    # async def add_newmessages(self, data):
    #     """add new message and send it"""
        
# -------------------------------------------------image---------------------------------
    # async def add_newimgs(self,data):
    #     """ add new image and send it """
    #     author=data['sender']
    #     author_user=UserModel.objects.filter(username=author)[0]
    #     message=MessagesModel.objects.create(user_model=author_user,img=data['message'])
        
    #     current_chat=get_current_chat(data['channels_id'])
    #     current_chat.messages.add(message)
    #     current_chat.save()
    #     content={
    #         "command":"add_imgs",
    #         "message":await self.img_to_json(message)

    #     }
    #     return self.chat_message(content)
    
    
# ------------------------------------------file----------------------------------------------
    # async def add_newfiles(self,data):
    #     """ add new file and send it  """
    #     author=data['sender']
    #     author_user=UserModel.objects.filter(username=author)[0]
    #     message=MessagesModel.objects.create(user_model=author_user,video=data['message'])
    #     current_chat=get_current_chat(data['channels_id'])
    #     current_chat.messages.add(message)
    #     current_chat.save()
    #     content={
    #         "command":"add_files",
    #         "message":await self.file_to_json(message)

    #     }
    #     return await self.chat_message(content)
    
    # async def file_to_json(self,message):
    #     return await {
    #         "author":message.user_model.username,
    #         "files":message.video,
    #         "time":str(message.message_dt),
    #         "user_image":message.user_model.profile_photo
    #     }
    

    # def add_newemojis(self,emoji):
    #     """ add new emoji and send it  """
    #     pass