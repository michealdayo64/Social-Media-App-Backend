from itertools import chain
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.conf import settings
import json
from account.serializers import UserSerializer
from message_app.utils import find_or_create_private_chat
from .models import PrivateChatRoom
from account.models import Accounts
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes  # type: ignore
from rest_framework import status  # type: ignore
from django.core import serializers
# Create your views here.

DEBUG = True


def private_chat_room_view(request, *args, **kwargs):
    context = {}
    user = request.user
    room_id = request.POST.get("room_id")
    if not user.is_authenticated:
        return HttpResponse("This user is not authenticated")

    if room_id:
        try:
            room = PrivateChatRoom.objects.get(pk=room_id)
            context['room'] = room
        except PrivateChatRoom.DoesNotExist:
            pass

    room1 = PrivateChatRoom.objects.filter(user1=user, is_active=True)
    room2 = PrivateChatRoom.objects.filter(user2=user, is_active=True)
    rooms = list(chain(room1, room2))
    m_and_f = []

    for room in rooms:
        if room.user1 == user:
            friend = room.user2
        else:
            friend = room.user1
        m_and_f.append({
            "message": "",
            "friend": friend
        })
    context["m_and_f"] = m_and_f
    context['debug'] = DEBUG
    context['debug_mode'] = settings.DEBUG

    return render(request, "message_app/message.html", context)


def create_or_return_private_chat(request, *args, **kwargs):
    user1 = request.user
    payload = {}
    if user1.is_authenticated:
        if request.method == "POST":
            user2_id = kwargs.get("user2_id")
            print(user2_id)
            try:
                user2 = Accounts.objects.get(pk=user2_id)
                chat = find_or_create_private_chat(user1, user2)
                print(chat.id)
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
        room1 = PrivateChatRoom.objects.filter(user1=user, is_active=True)
        room2 = PrivateChatRoom.objects.filter(user2=user, is_active=True)
        rooms = list(chain(room1, room2))

        m_and_f = []

        for room in rooms:
            if room.user1 == user:
                friend = room.user2
                user_serializer = UserSerializer(
                    friend, context={'request': request}).data
            else:
                friend = room.user1
                user_serializer = UserSerializer(
                    friend, context={'request': request}).data
            m_and_f.append({
                "message": "",
                "friend": user_serializer
            })
        payload = {
            "m_and_f": m_and_f
        }
        return Response(data=payload, status=status.HTTP_200_OK)
    else:
        payload["msg"] = "User not authenticated"
        return Response(data=payload, status=status.HTTP_400_BAD_REQUEST)
