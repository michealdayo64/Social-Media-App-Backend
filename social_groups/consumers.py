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
        