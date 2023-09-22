from django.http import HttpResponse
from django.shortcuts import redirect, render
from friend_app.models import FriendsList, FriendRequest
from account.models import Accounts

# Create your views here.

'''
All User
'''


def friend_index(request):
    user = request.user
    context = {}
    if user.is_authenticated:
        user_id = user.id
        all_user = Accounts.objects.exclude(id=user_id)

        accounts = []
        auth_user_friend_list = FriendsList.objects.get(user=user)
        for account in all_user:
            print(auth_user_friend_list.friends.all().count())
            accounts.append(
                (account, auth_user_friend_list.is_mutual_friend(account), auth_user_friend_list.friends.all().count()))
        print(accounts)
        context = {
            'accounts': accounts
        }
        return render(request, 'friend_app/friend.html', context)
    else:
        print("User not authenticated")
    return render(request, 'friend_app/friend.html', context)


def send_friend_request(request, *args, **kwargs):
    user = request.user
    #context = {}
    if user.is_authenticated:
        user_id = kwargs.get("user_id")
        reciever = Accounts.objects.get(user=user_id)
        try:
            # Get any friend requests (active and not-active)
            friend_requests = FriendRequest.objects.filter(
                sender=user, reciever=reciever)
            # find if any of them are active
            try:
                for request in friend_requests:
                    if request.is_active:
                        raise Exception(
                            "You already sent them a friend request")
                # If none is active, then create a new friend request
                friend_request = FriendRequest(sender=user, reciever=reciever)
                friend_request.save()
                return redirect("friend-index")
            except Exception as e:
                return HttpResponse("You can't view someone elses friend requests")
        except FriendRequest.DoesNotExist:
            # If none is active, then create a new friend request
            friend_request = FriendRequest(sender=user, reciever=reciever)
            friend_request.save()
            return redirect("friend-index")
    else:
        print("User not authenticated")
        return redirect("friend-index")
