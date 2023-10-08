from itertools import chain
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.conf import settings
from .models import PrivateChatRoom
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
            room = PrivateChatRoom.objects.get(pk = room_id)
            print(room)
            context['room'] = room
        except PrivateChatRoom.DoesNotExist:
            pass

    room1 = PrivateChatRoom.objects.filter(user1 = user, is_active = True)
    room2 = PrivateChatRoom.objects.filter(user2 = user, is_active = True)

    rooms = list(chain(room1, room2))
    print(rooms)
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
