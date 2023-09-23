from django.http import HttpResponse
from django.shortcuts import redirect, render
from friend_app.models import FriendsList, FriendRequest
from account.models import Accounts
from .friendRequestStatus import FriendRequestStatus
from .utils import get_friend_request_or_false

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
        """is_self = True
        is_friend = False
        request_sent = FriendRequestStatus.NO_REQUEST_SENT.value
        friend_requests = None"""
        
        for account in all_user:
            try:
                auth_user_friend_list = FriendsList.objects.get(user=account)
            except FriendsList.DoesNotExist:
                auth_user_friend_list = FriendsList(user = account)
                auth_user_friend_list.save()

            is_friend = False
            request_sent = FriendRequestStatus.NO_REQUEST_SENT.value
            friend_requests = None

            friends = auth_user_friend_list.friends.all()
            if friends.filter(pk = user.id):
                is_friend = True
            else:
                is_friend = False

                #CASE1: Request has been sent from THEM to YOU:
                #FriendRequestStatus.THEM_SENT_TO_YOU
                if get_friend_request_or_false(sender = account, reciever = user) != False:
                    request_sent = FriendRequestStatus.THEM_SENT_TO_YOU.value

                #CASE1: Request has been sent from YOU to THEM:
                #FriendRequestStatus.YOU_SENT_TO_THEM
                elif get_friend_request_or_false(sender = user, reciever = account) != False:
                    request_sent = FriendRequestStatus.YOU_SENT_TO_THEM.value

                #CASE1: No Request has been sent. FriendRequestStatus.NO_REQUEST_SENT
                else:
                    request_sent = FriendRequestStatus.NO_REQUEST_SENT.value
            try:
                friend_requests = FriendRequest.objects.filter(reciever = user, is_active = True)
            except:
                pass
            
            print(is_friend, request_sent, friend_requests)
            accounts.append(
                (account, auth_user_friend_list.is_mutual_friend(account), auth_user_friend_list.friends.all().count(), is_friend, request_sent, friend_requests))
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
