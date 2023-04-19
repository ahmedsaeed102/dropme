import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncWebsocketConsumer,WebsocketConsumer

# our chat commands
class ChatConsumer(AsyncWebsocketConsumer):
    def fetch_10recent_messages(self,messages):
        """ load recent 10 message and send it to you """
        pass
    def add_newmessages(self,message):
        """ add new typed message and send it  """
        pass
    
    def add_newfiles(self,files):
        """ add new file and send it  """
        pass

    def add_newemojis(self,emoji):
        """ add new emoji and send it  """
        pass


    commands={

        """ to filter the specific operation when we used receive method"""
        'fetch_messages':fetch_10recent_messages,
        'add_messages':add_newmessages,
        'add_files':add_newfiles,
        'add_newemojis':add_newemojis
    }
    def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"

        # Join room group
        async_to_sync(self.channel_layer.group_add(self.room_group_name, self.channel_name)) 

        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard(self.room_group_name, self.channel_name))

    # Receive message from WebSocket
    def receive(self, text_data):
        # grap data 
        data = json.loads(text_data)
        # used to handle logic of every command 
        self.commands[data['command']](self,data)

    
    def send_messages(self,message):
        message = data["message"]

        # Send message to room group
        async_to_sync(self.channel_layer.group_send(
            self.room_group_name, {"type": "chat.message", "message": message}
        ))

    # Receive message from room group
    def chat_message(self, event):
        message = event["message"]

        # Send message to WebSocket
        self.send(text_data=json.dumps({"message": message}))