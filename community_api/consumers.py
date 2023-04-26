import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncWebsocketConsumer,WebsocketConsumer
from community_api.models import MessagesModel
from users_api.models import UserModel
from .views import last_10_messages,get_current_chat
from channels.db import database_sync_to_async


class ChatConsumer(AsyncWebsocketConsumer):
    def get_num_of_message(self,num):
        """"it return the number of total messages inside specific channels"""
        num=MessagesModel.get_messages_num()
        return num

    async def fetch_10recent_messages(self,data):
        """ load recent 10 message and send it to you """
        messages=last_10_messages(data['channels_id'])
        content={
            'messages':await self.messages_to_json(messages)
        }
        await self.send_messages(content)

# ------------------------------------------message--------------------------------------------------------
    async def add_newmessages(self,data):
        """ add new typed message and send it  """
        author=data['sender']
        author_user=UserModel.objects.filter(username=author)[0]
        message=MessagesModel.objects.create(user_model=author_user,content=data['message'])
        current_chat=get_current_chat(data['channels_id'])
        current_chat.messages.add(message)
        current_chat.save()
        content={
            "command":"add_messages",
            "message":await self.message_to_json(message)

        }
        return await self.chat_message(content)
    

    async def messages_to_json(self,messages):
        """ convert all messages to json  """
        result=[]
        for message in messages:
            result.append(await self.message_to_json(message))
        return result
    

    async def message_to_json(self,message):
        """ convert one message to json"""
        return await {
            "author":message.user_model.username,
            "content":message.content,
            "time":str(message.message_dt),
            "user_image":message.user_model.profile_photo
        }
# -------------------------------------------------image---------------------------------
    async def add_newimgs(self,data):
        """ add new image and send it  """
        author=data['sender']
        author_user=UserModel.objects.filter(username=author)[0]
        message=MessagesModel.objects.create(user_model=author_user,img=data['message'])
        
        current_chat=get_current_chat(data['channels_id'])
        current_chat.messages.add(message)
        current_chat.save()
        content={
            "command":"add_imgs",
            "message":await self.img_to_json(message)

        }
        return self.chat_message(content)
    
    async def img_to_json(self,message):
        return await {
            "author":message.user_model.username,
            "image":message.img,
            "time":str(message.message_dt),
            "user_image":message.user_model.profile_photo
        }
    
# ------------------------------------------file----------------------------------------------
    async def add_newfiles(self,data):
        """ add new file and send it  """
        author=data['sender']
        author_user=UserModel.objects.filter(username=author)[0]
        message=MessagesModel.objects.create(user_model=author_user,video=data['message'])
        current_chat=get_current_chat(data['channels_id'])
        current_chat.messages.add(message)
        current_chat.save()
        content={
            "command":"add_files",
            "message":await self.file_to_json(message)

        }
        return await self.chat_message(content)
    
    async def file_to_json(self,message):
        return await {
            "author":message.user_model.username,
            "files":message.video,
            "time":str(message.message_dt),
            "user_image":message.user_model.profile_photo
        }
    

# ---------------------------------emoji----------------------------------------

    def add_newemojis(self,emoji):
        """ add new emoji and send it  """
        pass

# our chat commands
    commands={

        """ to filter the specific operation when we used receive method"""
        'fetch_messages':fetch_10recent_messages,
        'add_messages':add_newmessages,
        'add_files':add_newfiles,
        'add_newemojis':add_newemojis,
        'add_imgs':add_newimgs
    }

    
    async def connect(self,event):
        print("connected",event)
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"

        # Join room group
        await database_sync_to_async(self.channel_layer.group_add(self.room_group_name, self.room_name)) 

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await database_sync_to_async(self.channel_layer.group_discard(self.room_group_name, self.room_name))
        print('disconnected', close_code)
    # Receive message from WebSocket
    async def receive(self, text_data):
        # grap data 
        data = json.loads(text_data)
        # used to handle logic of every command 
        self.commands[data['command']](self,data)

    
    async def send_messages(self,message):

        # Send message to room group
        await database_sync_to_async(self.channel_layer.group_send(
            self.room_group_name, {"type": "chat.message", "message": message}
        ))
    


    async def send_message(self, message):
        """ take the content and then send directly the message"""
        await self.send(text_data=json.dumps(message))

    # Receive message from room group
    async def chat_message(self, event):
        message = event["message"]

        # Send message to WebSocket
        # {"message": message}
        await self.send(text_data=json.dumps(message))