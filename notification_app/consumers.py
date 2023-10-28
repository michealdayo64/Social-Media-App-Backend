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
                if payload == None:
                    await self.general_pagination_exhausted()
                else:
                    payload = json.loads(payload)
                    await self.send_general_notifications_payload(payload['notifications'], payload['new_page_number'])
            elif command == "accept_friend_request":
                notification_id = content['notification_id']
                payload = await accept_friend_request(self.scope['user'], notification_id)
                if payload == None:
                    raise ClientError("UNKNOWN_ERROR", "Something went wrong. Try refreshing the browser.")
                else:
                    payload = json.loads(payload)
                    await self.send_updated_friend_request_notification(payload['notification'])
            elif command == "decline_friend_request":
                notification_id = content['notification_id']
                payload = await decline_friend_request(self.scope['user'], notification_id)
                if payload == None:
                    raise ClientError("UNKNOWN_ERROR", "Something went wrong. Try refreshing the browser.")
                else:
                    payload = json.loads(payload)
                    await self.send_updated_friend_request_notification(payload['notification'])
            elif command == "refresh_general_notifications":
                payload = await refresh_general_notifications(self.scope["user"], content['oldest_timestamp'], content['newest_timestamp'])
                if payload == None:
                    raise ClientError("UNKNOWN_ERROR", "Something went wrong. Try refreshing the browser.")
                else:
                    payload = json.loads(payload)
                    await self.send_general_refreshed_notifications_payload(payload['notifications'])
            elif command == "get_new_general_notifications":
                payload = await get_new_general_notifications(self.scope["user"], content.get("newest_timestamp", None))
                if payload != None:
                    payload = json.loads(payload)
                    await self.send_new_general_notifications_payload(payload['notifications'])
        except: 
            pass


    async def disconnect(self, code):
        """
        Called when the websockect closes for any reason
        """
        print("PublicChatConsumer: diconnect")


    async def general_pagination_exhausted(self):
        """
        Called by receive_json when pagination is exhausted for general notifications
        """
        #print("General Pagination DONE... No more notifications.")
        await self.send_json(
            {
                "general_msg_type": GENERAL_MSG_TYPE_PAGINATION_EXHAUSTED,
            },
        )

    async def send_general_notifications_payload(self, notifications, new_page_number):
        """
        Called by receive_json when ready to send a json array of the notifications
        """
        #print("NotificationConsumer: send_general_notifications_payload")
        await self.send_json(
            {
                "general_msg_type": GENERAL_MSG_TYPE_NOTIFICATIONS_PAYLOAD,
                "notifications": notifications,
                "new_page_number": new_page_number,
            },
        )

    async def send_updated_friend_request_notification(self, notification):
        """
        After a friend request is accepted or declined, send the updated notification to template
        payload contains 'notification' and 'response':
        1. payload['notification']
        2. payload['response']
        """
        await self.send_json(
            {
                "general_msg_type": GENERAL_MSG_TYPE_UPDATED_NOTIFICATION,
                "notification": notification,
            },
        )

    async def send_general_refreshed_notifications_payload(self, notifications):
        """
        Called by receive_json when ready to send a json array of the notifications
        """
        #print("NotificationConsumer: send_general_refreshed_notifications_payload: " + str(notifications))
        await self.send_json(
            {
                "general_msg_type": GENERAL_MSG_TYPE_NOTIFICATIONS_REFRESH_PAYLOAD,
                "notifications": notifications,
            },
        )



@database_sync_to_async
def get_general_notifications(user, page_number):
    """
    Get General Notifications with Pagination (next page of results).
    This is for appending to the bottom of the notifications list.
    General Notifications are:
    1. FriendRequest
    2. FriendList
    """
    payload = {}
    if user.is_authenticated:
        friend_request_ct = ContentType.objects.get_for_model(FriendRequest)
        friend_list_ct = ContentType.objects.get_for_model(FriendsList)
        notifications = Notification.objects.filter(target=user, content_type__in=[friend_request_ct, friend_list_ct]).order_by('-timestamp')
        p = Paginator(notifications, DEFAULT_NOTIFICATION_PAGE_SIZE)
        
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


@database_sync_to_async
def accept_friend_request(user, notification_id):
    """
    Accept a friend request
    """
    payload = {}
    if user.is_authenticated:
        try:
            notification = Notification.objects.get(pk=notification_id)
            friend_request = notification.content_object
            # confirm this is the correct user
            if friend_request.reciever == user:
                # accept the request and get the updated notification
                updated_notification = friend_request.accept()

                # return the notification associated with this FriendRequest
                s = LazyNotificationEncoder()
                payload['notification'] = s.serialize([updated_notification])[0]
                return json.dumps(payload)
        except Notification.DoesNotExist:
            raise ClientError("AUTH_ERROR", "An error occurred with that notification. Try refreshing the browser.")
    return None

@database_sync_to_async
def decline_friend_request(user, notification_id):
    """
    Decine a friend request
    """
    payload = {}
    if user.is_authenticated:
        try:
            notification = Notification.objects.get(pk=notification_id)
            friend_request = notification.content_object
            # confirm this is the correct user
            if friend_request.reciever == user:
                # accept the request and get the updated notification
                updated_notification = friend_request.decline()

                # return the notification associated with this FriendRequest
                s = LazyNotificationEncoder()
                payload['notification'] = s.serialize([updated_notification])[0]
                return json.dumps(payload)
        except Notification.DoesNotExist:
            raise ClientError("AUTH_ERROR", "An error occurred with that notification. Try refreshing the browser.")
    return None


@database_sync_to_async
def refresh_general_notifications(user, oldest_timestamp, newest_timestamp):
	"""
	Retrieve the general notifications newer than the oldest one on the screen and younger than the newest one the screen.
	The result will be: Notifications currently visible will be updated
	"""
	payload = {}
	if user.is_authenticated:
		oldest_ts = oldest_timestamp[0:oldest_timestamp.find("+")] # remove timezone because who cares
		oldest_ts = datetime.strptime(oldest_ts, '%Y-%m-%d %H:%M:%S.%f')
		newest_ts = newest_timestamp[0:newest_timestamp.find("+")] # remove timezone because who cares
		newest_ts = datetime.strptime(newest_ts, '%Y-%m-%d %H:%M:%S.%f')
		friend_request_ct = ContentType.objects.get_for_model(FriendRequest)
		friend_list_ct = ContentType.objects.get_for_model(FriendsList)
		notifications = Notification.objects.filter(target=user, content_type__in=[friend_request_ct, friend_list_ct], timestamp__gte=oldest_ts, timestamp__lte=newest_ts).order_by('-timestamp')

		s = LazyNotificationEncoder()
		payload['notifications'] = s.serialize(notifications)
	else:
		raise ClientError("AUTH_ERROR", "User must be authenticated to get notifications.")

	return json.dumps(payload) 