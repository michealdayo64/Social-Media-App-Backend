from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.contenttypes.models import ContentType
from friend_app.models import FriendRequest, FriendsList
from .models import Notification
from django.core.paginator import Paginator
from .constant import *
from .utils import LazyNotificationEncoder
from social_groups.exception import ClientError
import json


class NotificationConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        """
        Called when the websocket is handshaking as part of initial connection
        """
        print("NotificationConsumer: connect: " + str(self.scope['user']))
        await self.accept()

        self.room_id = None

    async def receive_json(self, content):
        """
        Called when we get a tex frame. Channels will json-decode the payload for us
        and pass it as the first argument
        """
        command = content.get("command", None)
        print("PublicChatConsumer: receive_json: " + str(command))
        try:
            if command == "get_general_notifications":
                payload = await get_general_notifications(self.scope["user"], content.get("page_number", None))
        except: 
            pass


    async def disconnect(self, code):
        """
        Called when the websockect closes for any reason
        """
        print("PublicChatConsumer: diconnect")



@database_sync_to_async
def get_general_notifications(user, page_number):
    """
    Get General Notifications with Pagination (next page of results).
    This is for appending to the bottom of the notifications list.
    General Notifications are:
    1. FriendRequest
    2. FriendList
    """
    if user.is_authenticated:
        friend_request_ct = ContentType.objects.get_for_model(FriendRequest)
        friend_list_ct = ContentType.objects.get_for_model(FriendsList)
        notifications = Notification.objects.filter(target=user, content_type__in=[friend_request_ct, friend_list_ct]).order_by('-timestamp')
        p = Paginator(notifications, DEFAULT_NOTIFICATION_PAGE_SIZE)

        payload = {}
        if len(notifications) > 0:
            if int(page_number) <= p.num_pages:
                s = LazyNotificationEncoder()
                serialized_notifications = s.serialize(p.page(page_number).object_list)
                payload['notifications'] = serialized_notifications
                new_page_number = int(page_number) + 1
                payload['new_page_number'] = new_page_number
        else:
            return None
    else:
        raise ClientError("AUTH_ERROR", "User must be authenticated to get notifications.")

    return json.dumps(payload)