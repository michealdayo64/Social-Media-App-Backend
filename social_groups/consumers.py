from channels.generic.websocket import AsyncJsonWebsocketConsumer


class GroupConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        """
        Called when the websocket is handshaking as part of initial connection
        """
        print("PublicChatConsumer: connect: " + str(self.scope['user']))
        await self.accept()

        self.room_id = None

    
    async def receive_json(self, content):
        """
        Called when we get a tex frame. Channels will json-decode the payload for us
        and pass it as the first argument
        """
        command = content.get("command", None)
        #message = content.get("message", None)
        print("PublicChatConsumer: receive_json: " + str(command))


    async def disconnect(self, code):
        """
        Called when the websockect closes for any reason
        """
        print("PublicChatConsumer: diconnect")


    async def chat_message(self, event):
        """
        Called when someone has messaged our chat
        """
        # Send a message down to the client
        print("PublicChatConsumer: chat_message from user #: " + str(event['user_id']))
        #timestamp = calculate_timestamp(timezone.now())
        await self.send_json({
            #"msg_type": MSG_TYPE_MESSAGE,
            #"profile_image": event['profile_image'],
            "username": event['username'],
            'user_id': event['user_id'],
            'message': event['message'],
            #"natural_timestamp": timestamp
        })
        