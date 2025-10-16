from itertools import chain
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.conf import settings
import json
from account.serializers import UserSerializer
from message_app.serializers import RoomChatMessageSerializer
from message_app.utils import calculate_timestamp, find_or_create_private_chat
from .models import PrivateChatRoom, RoomChatMessage, UnreadChatRoomMessages
from account.models import Accounts
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes  # type: ignore
from rest_framework import status  # type: ignore
from account.views import get_tokens_for_user
from friend_app.models import FriendsList
from datetime import datetime
import pytz
# Create your views here.

DEBUG = True


def private_chat_room_view(request, *args, **kwargs):
    context = {}
    user = request.user
    room_id = request.GET.get("room_id")
    if not user.is_authenticated:
        return HttpResponse("This user is not authenticated")

    if room_id:
        try:
            room = PrivateChatRoom.objects.get(pk=room_id)
            context['room'] = room
        except PrivateChatRoom.DoesNotExist:
            pass

    token = get_tokens_for_user(user)
    user_access_token = token['token']['access']
    # print(user_access_token)
    context["user_access_token"] = user_access_token

    # room1 = PrivateChatRoom.objects.filter(user1=user, is_active=True)
    # room2 = PrivateChatRoom.objects.filter(user2=user, is_active=True)
    # rooms = list(chain(room1, room2))

    m_and_f = get_recent_chatroom_messages(user)
    context["m_and_f"] = m_and_f
    context['debug'] = DEBUG
    context['debug_mode'] = settings.DEBUG

    return render(request, "message_app/message.html", context)


def friendsWithMessage(request):
    context = {}
    user = request.user
    if user.is_authenticated:
        m_and_f = get_recent_chatroom_messages(user)
    context["m_and_f"] = m_and_f

    return render(request, 'message_app/friends_message.html', context)


def get_recent_chatroom_messages(user):
    """
        sort in terms of most recent chats (users that you most recently had conversations with)
        """
    # 1. Find all the rooms this user is a part of
    rooms1 = PrivateChatRoom.objects.filter(user1=user, is_active=True)
    rooms2 = PrivateChatRoom.objects.filter(user2=user, is_active=True)

    # 2. merge the lists
    rooms = list(chain(rooms1, rooms2))

    # 3. find the newest msg in each room
    m_and_f = []
    for room in rooms:
        # Figure out which user is the "other user" (aka friend)
        if room.user1 == user:
            friend = room.user2
            room_id = room.id
            # print(room)
        else:
            friend = room.user1
            room_id = room.id
            # print(room)
        # confirm you are even friends (in case chat is left active somehow)
        friend_list = FriendsList.objects.get(user=user)
        if not friend_list.is_mutual_friend(friend):
            chat = find_or_create_private_chat(user, friend)
            chat.is_active = False
            chat.save()
        else:
            # find newest msg from that friend in the chat room
            try:
                message = RoomChatMessage.objects.filter(
                    room=room, user=friend).latest("timestamp")
            except RoomChatMessage.DoesNotExist:
                # create a dummy message with dummy timestamp
                today = datetime(
                    year=1950,
                    month=1,
                    day=1,
                    hour=1,
                    minute=1,
                    second=1,
                    tzinfo=pytz.UTC
                )
                message = RoomChatMessage(
                    user=friend,
                    room=room,
                    timestamp=today,
                    content="",
                )
            m_and_f.append({
                'message': message,
                'friend': friend,
                'room_id': room_id
            })

    return sorted(m_and_f, key=lambda x: x['message'].timestamp, reverse=True)


'''def getUnreadChatCount(request, id):
    user = request.user
    payload = {}
    count = 0
    if user.is_authenticated:
        user_id = Accounts.objects.get(id = id)
        #user_acc = FriendsList.objects.get(user = user)
        room_id = find_or_create_private_chat(user, user_id)
        countUnread = UnreadChatRoomMessages.objects.filter(room = room_id.id, user = user_id)
        for i in countUnread:
            count = i.count
            

        rooms1 = PrivateChatRoom.objects.filter(user1=user, is_active=True)
        rooms2 = PrivateChatRoom.objects.filter(user2=user, is_active=True)

        # 2. merge the lists
        rooms = list(chain(rooms1, rooms2))

        for room in rooms:
            # Figure out which user is the "other user" (aka friend)
            if room.user1 == user:
                friend = room.user2
                room_id = room.id
                countUnread = UnreadChatRoomMessages.objects.filter(room = room_id, user = friend)
                for i in countUnread:
                    countR = i.count
                    print(countR)
            else:
                friend = room.user1
                room_id = room.id
                countUnread = UnreadChatRoomMessages.objects.filter(room = room_id, user = friend)
                for i in countUnread:
                    countR = i.count
                    print(countR)
            count.append(countR)
        print(count)
        payload['counter'] = count
    return JsonResponse((payload), content_type="application/json", safe=False)'''


def create_or_return_private_chat(request, *args, **kwargs):
    user1 = request.user
    payload = {}
    if user1.is_authenticated:
        if request.method == "POST":
            user2_id = kwargs.get("user2_id")
            try:
                user2 = Accounts.objects.get(pk=user2_id)
                chat = find_or_create_private_chat(user1, user2)
                payload['response'] = "Successfully got the chat"
                payload['chatroom_id'] = chat.id
            except Accounts.DoesNotExist:
                payload['response'] = "Unable to start a chat with that user."
    else:
        payload['response'] = "You can't start a chat if you are not authenticated."
    return HttpResponse(json.dumps(payload), content_type="application/json")


"""
Get ALL Chat Friends List 
"""


@api_view(['POST',])
@permission_classes((IsAuthenticated,))
def createOrReturnPrivateChatApi(request, *args, **kwargs):
    user1 = request.user
    payload = {}
    if user1.is_authenticated:
        if request.method == "POST":
            user2_id = kwargs.get("user2_id")
            try:
                user2 = Accounts.objects.get(pk=user2_id)
                chat = find_or_create_private_chat(user1, user2)
                payload['msg'] = "Successfully got the chat"
                payload['chatroom_id'] = chat.id
                return Response(data=payload, status=status.HTTP_200_OK)
            except Accounts.DoesNotExist:
                payload['msg'] = "Unable to start a chat with that user."
                return Response(data=payload, status=status.HTTP_400_BAD_REQUEST)
    else:
        payload['msg'] = "You can't start a chat if you are not authenticated."
    return Response(data=payload, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET',])
@permission_classes((IsAuthenticated,))
def getFriendsChatList(request):
    payload = {}
    user = request.user
    if user.is_authenticated:
        # getUser = Accounts.objects.get(pk = user.id)
        m_and_f = get_recent_chatroom_messages(user)
        serializer_data = []
        for item in m_and_f:
            messages = RoomChatMessageSerializer(item['message']).data
            friends = UserSerializer(item['friend']).data
            time = item['message'].timestamp

            serializer_data.append({
                'message': messages,
                'friend': friends,
                'room': item['room_id'],
                'time': calculate_timestamp(time)
            })
        payload = {
            "m_and_f": serializer_data
        }
        return Response(data=payload, status=status.HTTP_200_OK)
    else:
        payload["msg"] = "User not authenticated"
        return Response(data=payload, status=status.HTTP_400_BAD_REQUEST)
