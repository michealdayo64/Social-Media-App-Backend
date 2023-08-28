from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from .models import GroupChatRoom
from .exception import ClientError
from .constant import *


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
        # message = content.get("message", None)
        print("PublicChatConsumer: receive_json: " + str(command))

        try:
            if command == "send":
                # if len(content['message'].lstrip()) == 0:
                # raise ClientError(422, "You can't send an empty message")
                # await self.send_room(content['room_id'], content['message'])
                pass
            elif command == "join":
                await self.join_room(content['room'])
            elif command == "leave":
                await self.leave_room(content['room'])
        except:
            pass

    async def disconnect(self, code):
        """
        Called when the websockect closes for any reason
        """
        print("PublicChatConsumer: diconnect")
        try:
            if self.room_id != None:
                await self.leave_room(self.room_id)
        except Exception:
            pass
        

    async def join_room(self, room_id):
        """
        Called by receive_json when someone sent a JOIN command
        """
        print("PublicChatConsumer: join_room")
        room = None
        is_auth = is_authenticated(self.scope['user'])

        try:
            room = await get_room_or_error(room_id)
        except ClientError as e:
            await self.handle_client_error(e)

        # Add user to "users" list for room
        if is_auth:
            await connect_user(room, self.scope['user'])

        # Store that we're in the room
        self.room_id = room.id

        # Add them to the group so they get room meaasges
        await self.channel_layer.group_add(
            room.group_name,
            self.channel_name
        )

        # Tell the client to finish opening the room
        await self.send_json(
            {
                "join": str(room.id),
                "username": self.scope['user'].username
            })

        num_connected_users = await get_num_connected_users(room)
        print(num_connected_users)

        await self.channel_layer.group_send(
            room.group_name,
            {
                "type": "connected.user.count",
                "connected_user_count": num_connected_users
            }
        )


    async def leave_room(self, room_id):
        """
        Called by receive_json when someone sent a leave command
        """
        print("PublicChatConsumer: leave_room")

        is_auth = is_authenticated(self.scope['user'])

        try:
            room = await get_room_or_error(room_id)
        except ClientError as e:
            await self.handle_client_error(e)

        #Remove user from 'users' list
        if is_auth:
            await disconnect_user(room, self.scope['user'])

        #Remove that we're in the room
        self.room_id = None

        #Remove them from the group so they no longer receive messages
        await self.channel_layer.group_discard(
            room.group_name,
            self.channel_name
        )

        num_connected_users = await get_num_connected_users(room)
        await self.channel_layer.group_send(
            room.group_name,
            {
                "type": "connected.user.count",
                "connected_user_count": num_connected_users
            }
        )

    async def connected_user_count(self, event):
        """
        Called to dend the number of connected userd to the room.
        This number is displayed in the room so other users know how many users are connected 
        to the chat
        """
        print("PublicChatConsumer: connected_user_count: count: " +
              str(event['connected_user_count']))
        await self.send_json({
            "msg_type": MSG_TYPE_CONNECTED_USER_COUNT,
            "connected_user_count": event['connected_user_count']
        })

    async def handle_client_error(self, e):
        """
        Called when a clienterror is raised.
        Sends error data to the UI
        """
        errorData = {}
        errorData['error'] = e.code
        if e.message:
            errorData['message'] = e.message
        return


def is_authenticated(user):
    if user.is_authenticated:
        return True
    return False


@database_sync_to_async
def get_room_or_error(room_id):
    """
    Tries to fetch a room for the user
    """
    try:
        room = GroupChatRoom.objects.get(pk=room_id)
    except GroupChatRoom.DoesNotExist:
        raise ClientError("Room_invalid", "Invalid room")
    return room


@database_sync_to_async
def connect_user(room, user):
    return room.connect_user(user)

@database_sync_to_async
def disconnect_user(room, user):
    return room.disconnect_user(user)


@database_sync_to_async
def get_num_connected_users(room):
    if room.users.all():
        return len(room.users.all())
    return 0
