from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.conf import settings
from account.models import Accounts
from friend_app.models import FriendsList
from django.core import files
import os
from django.core.files.storage import FileSystemStorage
import json
import base64


# Create your views here.
TEMP_PROFILE_IMAGE_NAME = "temp_profile_image.png"


def profile_index(request):
    user = request.user
    if user.is_authenticated:
        user_id = user.id
        account = get_object_or_404(Accounts, pk=user_id)
        friend_list = FriendsList.objects.get(user=account)
        friends = friend_list.friends.all()
        context = {
            'account': account,
            'friends': friends
        }
    return render(request, 'profile_app/profile.html', context)


def edit_profile(request, *args, **kwargs):
    context = {}
    user = request.user
    if user.is_authenticated:
        user_id = user.id
        account = get_object_or_404(Accounts, pk=user_id)
        friend_list = FriendsList.objects.get(user=account)
        friends = friend_list.friends.all()
        context["account"] = account
        context["friends"] = friends
        if request.method == 'POST':
            email = request.POST.get("email")
            username = request.POST.get("username")

            account.email = email
            account.username = username
            account.save()
            return redirect("profile-index")
        else:
            print("It is not a post")
    else:
        print("User not authenticated")
    return render(request, 'profile_app/edit_profile.html', context)

def save_temp_profile_image_from_base64String(imageString, user):
    INCORRECT_PADDING_EXCEPTION = "incorrect padding"
    try:
        if not os.path.exists(settings.TEMP):
            os.mkdir(settings.TEMP)
        if not os.path.exists(f"{settings.TEMP}/{user.pk}"):
            os.mkdir(f"{settings.TEMP}/{user.pk}")
        url = os.path.join(f"{settings.TEMP}/{user.pk}",
                           TEMP_PROFILE_IMAGE_NAME)
        storage = FileSystemStorage(location=url)
        print(storage)
        img = base64.b64decode(imageString)
        with storage.open("", "wb+") as destination:
            destination.write(img)
            destination.close()
        return url
    except Exception as e:
        if str(e) == INCORRECT_PADDING_EXCEPTION:
            imageString += "=" * ((4 - len(imageString) % 4) % 4)
            return save_temp_profile_image_from_base64String(imageString, user)
    return None

def edit_profile_image(request):
    payload = {}
    user = request.user
    if user.is_authenticated:
        try:
            ns = json.loads(request.body)
            imageString = ns.get('image')
            url = save_temp_profile_image_from_base64String(imageString, user)
            user.profile_image.delete()
            user.profile_image.save(
                    "profile_image.png", files.File(open(url, "rb")))
            user.save()
            payload['result'] = "success"
            os.remove(url)
        except Exception as e:
            payload["result"] = "error"
            payload["exception"] = str(e)
    return HttpResponse(json.dumps(payload), content_type="application/json", safe=False)