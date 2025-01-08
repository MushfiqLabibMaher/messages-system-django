# # class ChatConsumer(AsyncWebsocketConsumer):

# #     async def connect(self):
# #         self.room_name = f"room_{self.scope['url_route']['kwargs']['room_name']}"
# #         await self.channel_layer.group_add(self.room_name, self.channel_name)

# #         await self.accept()

# #     async def disconnect(self, code):
# #         await self.channel_layer.group_discard(self.room_name, self.channel_name)
# #         self.close(code)

# #     async def receive(self, text_data):
# #         # print("Recieved Data")
# #         data_json = json.loads(text_data)
# #         # print(data_json)

# #         event = {"type": "send_message", "message": data_json}

# #         await self.channel_layer.group_send(self.room_name, event)

# #     async def send_message(self, event):
# #         data = event["message"]
# #         await self.create_message(data=data)

# #         response = {"sender": data["sender"], "message": data["message"]}

# #         await self.send(text_data=json.dumps({"message": response}))

# #     @database_sync_to_async
# #     def create_message(self, data):
# #         get_room = Room.objects.get(room_name=data["room_name"])

# #         if not Message.objects.filter(
# #             message=data["message"], sender=data["sender"]
# #         ).exists():
# #             new_message = Message.objects.create(
# #                 room=get_room, message=data["message"], sender=data["sender"]
# #             )




import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from django.db import connections
from asgiref.sync import sync_to_async

# Set up logging
logger = logging.getLogger(__name__)

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """
        Handles WebSocket connection and adds the user to the room group.
        """
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f"chat_{self.room_name}"

        # Join the room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        """
        Handles WebSocket disconnection and removes the user from the room group.
        """
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        """
        Handles receiving messages from WebSocket and broadcasting them to the room group.
        """
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        sender = text_data_json['sender']

        # Save the message to the database
        room_exists = await self.save_message(self.room_name, sender, message)

        if room_exists:
            # Broadcast the message to the room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'sender': sender
                }
            )
        else:
            # Send a message back to the sender indicating the room does not exist
            await self.send(text_data=json.dumps({
                'message': 'Room does not exist.',
                'sender': 'System'
            }))

    async def chat_message(self, event):
        """
        Handles receiving messages from the room group and sending them to WebSocket.
        """
        message = event['message']
        sender = event['sender']

        # Send the message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'sender': sender
        }))

    @sync_to_async
    def save_message(self, room_name, sender, message):
        """
        Saves the message to the database using raw SQL.
        """
        with connections['test'].cursor() as cursor:
            try:
                # Check if the room_name exists in the 'admin' table
                cursor.execute("SELECT id FROM admin WHERE room_name = %s", [room_name])
                room = cursor.fetchone()

                if not room:
                    # Room doesn't exist
                    return False

                # Now that the room_name exists, insert the message into the 'chat_message' table
                cursor.execute("""
                    INSERT INTO chat_message (room_name_db, sender, message)
                    VALUES (%s, %s, %s)
                """, [room_name, sender, message])

                return True

            except Exception as e:
                logger.error(f"Error saving message: {str(e)}")
                return False