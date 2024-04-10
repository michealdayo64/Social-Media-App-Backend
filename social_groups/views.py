from django.shortcuts import render
from django.conf import settings
from .models import GroupChatRoom
import random
import time
from agora_token_builder import RtcTokenBuilder
from django.conf import settings
from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
from account.models import Accounts

# Create your views here.
DEBUG = False

"""
Group Chat List
"""


def group_list(request):
    user = request.user
    if user.is_authenticated:
        group_list = GroupChatRoom.objects.all()
        context = {
            'group_list': group_list
        }
    return render(request, 'group_list.html', context)


"""
Group Chat
"""


def group_detail(request, id):
    room_id = GroupChatRoom.objects.get(id=id)
    user = request.user
    context = {
        'room_id': room_id.pk,
        'room_detail': room_id,
        'debug_mode': settings.DEBUG,
        'debug': DEBUG,
        'user': user
    }
    return render(request, 'group_detail.html', context)


def roomCall(request):
    return render(request, 'call_room.html')


def getToken(request):
    appId = settings.APP_ID
    app_certificate = settings.APP_CERTIFICATE
    channel_name = request.GET.get("channel")
    uid = random.randint(1, 230)
    expirationTimeSeconds = 3600 * 24
    currentTimeStamp = time.time()
    privilegeExpiredTs = currentTimeStamp + expirationTimeSeconds
    role = 1
    token = RtcTokenBuilder.buildTokenWithUid(
        appId, app_certificate, channel_name, uid, role, privilegeExpiredTs)
    return JsonResponse({"token": token, "uid": uid, "appid": appId}, safe=False)


@csrf_exempt
def createMember(request):
    data = {}
    getData = json.loads(request.body)
    name = getData['username']
    uid = getData['UID']
    room_name = getData['room_name']
    user_id = request.user.id
    acc = Accounts.objects.get(pk=user_id)
    acc.uid = uid
    acc.save()

    data = {
        "name": name,
        'room_name': room_name
    }
    return JsonResponse(data=data, safe=False)


def getMember(request):
    pass
