from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from friend_app.models import FriendsList, FriendRequest
from account.models import Accounts
from .friendRequestStatus import FriendRequestStatus
from account.serializers import UserSerializer
from .utils import get_friend_request_or_false
from rest_framework.decorators import api_view, permission_classes  # type: ignore
from rest_framework.permissions import IsAuthenticated  # type: ignore
from rest_framework.response import Response  # type: ignore
from rest_framework import status  # type: ignore
from django.core import serializers
import json

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

        for account in all_user:
            try:
                auth_user_friend_list = FriendsList.objects.get(user=account)
                friends = auth_user_friend_list.friends.all()
            except FriendsList.DoesNotExist:
                auth_user_friend_list = FriendsList(user=account)
                auth_user_friend_list.save()

            if friends.filter(pk=user.id):
                is_friend = True
            else:
                is_friend = False
            request_sent = FriendRequestStatus.NO_REQUEST_SENT.value
            pending_friend_request_id = None

            # CASE1: Request has been sent from THEM to YOU:
            # FriendRequestStatus.THEM_SENT_TO_YOU
            if get_friend_request_or_false(sender=account, reciever=user) != False:
                request_sent = FriendRequestStatus.THEM_SENT_TO_YOU.value
                pending_friend_request_id = get_friend_request_or_false(
                    sender=account, reciever=user
                ).id

            # CASE1: Request has been sent from YOU to THEM:
            # FriendRequestStatus.YOU_SENT_TO_THEM
            elif get_friend_request_or_false(sender=user, reciever=account) != False:
                request_sent = FriendRequestStatus.YOU_SENT_TO_THEM.value

            # CASE1: No Request has been sent. FriendRequestStatus.NO_REQUEST_SENT
            else:
                request_sent = FriendRequestStatus.NO_REQUEST_SENT.value

            accounts.append(
                (account, is_friend, auth_user_friend_list.friends.all().count(), request_sent, pending_friend_request_id))
        context = {
            'accounts': accounts
        }
        return render(request, 'friend_app/friend.html', context)
    else:
        print("User not authenticated")
    return render(request, 'friend_app/friend.html', context)


"""
Friends Details Page
"""


def friend_detail(request, *args, **kwargs):
    user = request.user
    context = {}
    if user.is_authenticated:
        user_id = kwargs.get("user_id")
        # print(user_id)
        account = get_object_or_404(Accounts, pk=user_id)
        context['account'] = account
        friend_list = FriendsList.objects.get(user=account)
        friends = friend_list.friends.all()
        context['friends'] = friends
        is_myfriend = friend_list.is_mutual_friend(user)
        context['is_myfriend'] = is_myfriend
        request_sent = FriendRequestStatus.NO_REQUEST_SENT.value
        context['request_sent'] = request_sent
        pending_friend_request_id = None
        # CASE1: Request has been sent from THEM to YOU:
        # FriendRequestStatus.THEM_SENT_TO_YOU
        if get_friend_request_or_false(sender=account, reciever=user) != False:
            request_sent = FriendRequestStatus.THEM_SENT_TO_YOU.value
            context['request_sent'] = request_sent
            pending_friend_request_id = get_friend_request_or_false(
                sender=account, reciever=user
            ).id
            context['pending_friend_request_id'] = pending_friend_request_id

        # CASE1: Request has been sent from YOU to THEM:
        # FriendRequestStatus.YOU_SENT_TO_THEM
        elif get_friend_request_or_false(sender=user, reciever=account) != False:
            request_sent = FriendRequestStatus.YOU_SENT_TO_THEM.value
            context['request_sent'] = request_sent
        # CASE1: No Request has been sent. FriendRequestStatus.NO_REQUEST_SENT
        else:
            request_sent = FriendRequestStatus.NO_REQUEST_SENT.value
            context['request_sent'] = request_sent
    return render(request, 'friend_app/friend_detail.html', context)


'''
Send Friend Request
'''


def send_friend_request(request, *args, **kwargs):
    user = request.user
    # context = {}
    if user.is_authenticated:
        user_id = kwargs.get("user_id")
        reciever = Accounts.objects.get(id=user_id)
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
                return redirect("friend-detail", user_id)
            except Exception as e:
                return HttpResponse("You can't view someone elses friend requests")
        except FriendRequest.DoesNotExist:
            # If none is active, then create a new friend request
            friend_request = FriendRequest(sender=user, reciever=reciever)
            friend_request.save()
            return redirect("friend-detail", user_id)
    else:
        print("User not authenticated")
        return redirect("friend-index")


'''
Accept Friend Request
'''


def accept_friend_request(request, *args, **kwargs):
    user = request.user
    if user.is_authenticated:
        pending_friend_id = kwargs.get("pending_friend_id")
        if pending_friend_id:
            friend_request = FriendRequest.objects.get(id=pending_friend_id)
            if friend_request.reciever == user:
                if friend_request:
                    friend_request.accept()
                    return redirect("friend-index")
                else:
                    print("Something went wrong")
            else:
                print("This is not your request to accept")
    else:
        print("User need to be login")


'''
Decline Friemd request
'''


def decline_friend_request(request, *args, **kwargs):
    user = request.user
    if user.is_authenticated:
        pending_friend_id = kwargs.get("pending_friend_id")
        if pending_friend_id:
            friend_request = FriendRequest.objects.get(id=pending_friend_id)
            if friend_request.reciever == user:
                if friend_request:
                    friend_request.decline()
                    return redirect("friend-index")
                else:
                    print("Something went wrong")
            else:
                print("This is not your request to accept")
    else:
        print("User need to be login")


'''
Cancel Friend Request
'''


def cancel_friend_request(request, *args, **kwargs):
    user = request.user
    if user.is_authenticated:
        user_id = kwargs.get("receiver_user_id")
        if user_id:
            receiver = Accounts.objects.get(pk=user_id)
            try:
                friend_requests = FriendRequest.objects.filter(
                    sender=user, reciever=receiver, is_active=True)
            except Exception as e:
                print("Nothing to cancel. Friend request deos not exist")

            # There should only be a single active friend request at any giving time.
            # Cancel them all just in case.
            if len(friend_requests) > 1:
                for request in friend_requests:
                    request.cancel()
                return redirect("friend-detail", user_id)
            else:
                # found the request. Now cancel it.
                friend_requests.first().cancel()
                return redirect("friend-detail", user_id)
        else:
            print("Unble to cancel friend request")
    else:
        print("you must be authenticated to cancel a friend")


'''
remove Friend
'''


def remove_friend(request, *args, **kwargs):
    user = request.user
    if user.is_authenticated:
        user_id = kwargs.get("receiver_user_id")
        if user_id:
            try:
                removee = Accounts.objects.get(pk=user_id)
                friend_list = FriendsList.objects.get(user=user)
                friend_list.unfriend(removee)
                return redirect("friend-index")
            except Exception as e:
                print(f"Something went wrong: {str(e)}")
        else:
            print("There was an error. Unable to remove that friend")
    else:
        print("You must be authenticated to remove a friend")


'''---------------------------------- FRIENDS APIS --------------------------------'''


# TOTAL NUMBER OF FRIENDS
@api_view(['GET',])
@permission_classes((IsAuthenticated,))
def total_num_friends_api(request):
    data = {}
    user_id = request.user
    user_friend = FriendsList.objects.get(user=user_id)
    friend_count = user_friend.friends.count()
    data = {
        'msg': int(friend_count)
    }
    return Response(data=data, status=status.HTTP_200_OK)


# TOTAL NUMBER OF FRIEND REQUESTS
@api_view(['GET',])
@permission_classes((IsAuthenticated,))
def total_num_friend_request_api(request):
    data = {}
    user = request.user
    if user.is_authenticated:
        num_request = FriendRequest.objects.filter(
            reciever=user, is_active=True)
        data = {
            'msg': int(num_request.count())
        }
    return Response(data=data, status=status.HTTP_200_OK)


# GET ALL USERS
@api_view(['GET',])
@permission_classes((IsAuthenticated,))
def get_all_user_api(request):
    data = {}
    user = request.user
    if user.is_authenticated:
        all_user = Accounts.objects.exclude(username=user)
        # print(all_user)
        accounts = []

        for account in all_user:
            try:
                auth_user_friend_list = FriendsList.objects.get(user=account)
                friends = auth_user_friend_list.friends.all()
            except FriendsList.DoesNotExist:
                auth_user_friend_list = FriendsList(user=account)
                auth_user_friend_list.save()

            if friends.filter(pk=user.id):
                is_friend = True
            else:
                is_friend = False
            request_sent = FriendRequestStatus.NO_REQUEST_SENT.value
            pending_friend_request_id = None

            # CASE1: Request has been sent from THEM to YOU:
            # FriendRequestStatus.THEM_SENT_TO_YOU
            if get_friend_request_or_false(sender=account, reciever=user) != False:
                request_sent = FriendRequestStatus.THEM_SENT_TO_YOU.value
                pending_friend_request_id = get_friend_request_or_false(
                    sender=account, reciever=user
                ).id

            # CASE1: Request has been sent from YOU to THEM:
            # FriendRequestStatus.YOU_SENT_TO_THEM
            elif get_friend_request_or_false(sender=user, reciever=account) != False:
                request_sent = FriendRequestStatus.YOU_SENT_TO_THEM.value

            # CASE1: No Request has been sent. FriendRequestStatus.NO_REQUEST_SENT
            else:
                request_sent = FriendRequestStatus.NO_REQUEST_SENT.value

            payload = {
                'pk': account.id,
                'username': account.username,
                'name': f'{account.first_name} {account.last_name}',
                'pic': f'{settings.BASE_URL}{account.profile_image.url}',
                'is_friend': is_friend,
                'request_sent': request_sent,
                'pending_friend_request_id': pending_friend_request_id
            }

            accounts.append(payload
                            )
        print(accounts)
        if (accounts):
            data = {
                'msg': (accounts)
            }
            return JsonResponse(data=data, status=status.HTTP_200_OK)
    else:
        data = {
            "msg": "User Not Authenticated"
        }
        return JsonResponse(data=data, status=status.HTTP_401_UNAUTHOrIZED)


'''
Send Friend Request API
'''


@api_view(['POST',])
@permission_classes((IsAuthenticated,))
def send_friend_request_api(request, *args, **kwargs):
    user = request.user
    payload = {}
    if user.is_authenticated:
        all_user = Accounts.objects.exclude(username=user)
    # print(all_user)
        accounts = []
        user_id = kwargs.get("user_id")
        reciever = Accounts.objects.get(id=user_id)
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
                for account in all_user:
                    try:
                        auth_user_friend_list = FriendsList.objects.get(
                            user=account)
                        friends = auth_user_friend_list.friends.all()
                    except FriendsList.DoesNotExist:
                        auth_user_friend_list = FriendsList(user=account)
                        auth_user_friend_list.save()

                    if friends.filter(pk=user.id):
                        is_friend = True
                    else:
                        is_friend = False
                    request_sent = FriendRequestStatus.NO_REQUEST_SENT.value
                    pending_friend_request_id = None

                    # CASE1: Request has been sent from THEM to YOU:
                    # FriendRequestStatus.THEM_SENT_TO_YOU
                    if get_friend_request_or_false(sender=account, reciever=user) != False:
                        request_sent = FriendRequestStatus.THEM_SENT_TO_YOU.value
                        pending_friend_request_id = get_friend_request_or_false(
                            sender=account, reciever=user
                        ).id

                    # CASE1: Request has been sent from YOU to THEM:
                    # FriendRequestStatus.YOU_SENT_TO_THEM
                    elif get_friend_request_or_false(sender=user, reciever=account) != False:
                        request_sent = FriendRequestStatus.YOU_SENT_TO_THEM.value

                    # CASE1: No Request has been sent. FriendRequestStatus.NO_REQUEST_SENT
                    else:
                        request_sent = FriendRequestStatus.NO_REQUEST_SENT.value

                    payload = {
                        'pk': account.id,
                        'username': account.username,
                        'name': f'{account.first_name} {account.last_name}',
                        'pic': f'{settings.BASE_URL}{account.profile_image.url}',
                        'is_friend': is_friend,
                        'request_sent': request_sent,
                        'pending_friend_request_id': pending_friend_request_id
                    }

                    accounts.append(payload
                                    )
                payload = {
                    'msg': 'Success',
                    'data': accounts,
                    'pending_request_id': friend_request.id

                }
                return Response(data=payload, status=status.HTTP_200_OK)
            except Exception as e:
                return HttpResponse("You can't view someone elses friend requests")
        except FriendRequest.DoesNotExist:
            # If none is active, then create a new friend request
            friend_request = FriendRequest(sender=user, reciever=reciever)
            friend_request.save()
            payload = {
                'msg': 'Success',
                'data': accounts,
                'pending_request_id': friend_request.id

            }
            return Response(data=payload, status=status.HTTP_200_OK)
    else:
        payload = {
            'msg': 'Not Authenticated',
        }
        return Response(data=payload, status=status.HTTP_401_UNAUTHORIZED)


'''
Accept Friend Request API
'''


@api_view(['POST',])
@permission_classes((IsAuthenticated,))
def accept_friend_request_api(request, *args, **kwargs):
    payload = {}
    user = request.user
    all_user = Accounts.objects.exclude(username=user)
    accounts = []
    if user.is_authenticated:
        pending_friend_id = kwargs.get("pending_friend_id")
        if pending_friend_id:
            friend_request = FriendRequest.objects.get(id=pending_friend_id)
            if friend_request.reciever == user:
                if friend_request:
                    friend_request.accept()
                    for account in all_user:
                        try:
                            auth_user_friend_list = FriendsList.objects.get(
                                user=account)
                            friends = auth_user_friend_list.friends.all()
                        except FriendsList.DoesNotExist:
                            auth_user_friend_list = FriendsList(user=account)
                            auth_user_friend_list.save()

                        if friends.filter(pk=user.id):
                            is_friend = True
                        else:
                            is_friend = False
                        request_sent = FriendRequestStatus.NO_REQUEST_SENT.value
                        pending_friend_request_id = None

                        # CASE1: Request has been sent from THEM to YOU:
                        # FriendRequestStatus.THEM_SENT_TO_YOU
                        if get_friend_request_or_false(sender=account, reciever=user) != False:
                            request_sent = FriendRequestStatus.THEM_SENT_TO_YOU.value
                            pending_friend_request_id = get_friend_request_or_false(
                                sender=account, reciever=user
                            ).id

                        # CASE1: Request has been sent from YOU to THEM:
                        # FriendRequestStatus.YOU_SENT_TO_THEM
                        elif get_friend_request_or_false(sender=user, reciever=account) != False:
                            request_sent = FriendRequestStatus.YOU_SENT_TO_THEM.value

                        # CASE1: No Request has been sent. FriendRequestStatus.NO_REQUEST_SENT
                        else:
                            request_sent = FriendRequestStatus.NO_REQUEST_SENT.value
                            data = {
                                'pk': account.id,
                                'username': account.username,
                                'name': f'{account.first_name} {account.last_name}',
                                'pic': f'{settings.BASE_URL}{account.profile_image.url}',
                                'is_friend': is_friend,
                                'request_sent': request_sent,
                                'pending_friend_request_id': pending_friend_request_id
                            }
                            accounts.append(data
                                            )
                    payload = {
                        'msg': 'Success',
                        'data': account
                    }
                    return Response(data=payload, status=status.HTTP_200_OK)
                else:
                    payload = {
                        'msg': 'no data found'
                    }
                    return Response(data=payload, status=status.HTTP_204_NO_C0NTENT)
            else:
                payload = {
                    'msg': 'This is not your request to accept'
                }
                return Response(data=payload, status=status.HTTP_204_NO_C0NTENT)
    else:
        payload = {
            'msg': 'User Not Authenticated'
        }
        return Response(data=payload, status=status.HTTP_401_UNAUTHORIZED)


'''
Decline Friemd request API
'''


@api_view(['POST',])
@permission_classes((IsAuthenticated,))
def decline_friend_request_api(request, *args, **kwargs):
    payload = {}
    user = request.user
    if user.is_authenticated:
        all_user = Accounts.objects.exclude(username=user)
        accounts = []
        pending_friend_id = kwargs.get("pending_friend_id")
        if pending_friend_id:
            friend_request = FriendRequest.objects.get(id=pending_friend_id)
            if friend_request.reciever == user:
                if friend_request:
                    friend_request.decline()
                    for account in all_user:
                        try:
                            auth_user_friend_list = FriendsList.objects.get(
                                user=account)
                            friends = auth_user_friend_list.friends.all()
                        except FriendsList.DoesNotExist:
                            auth_user_friend_list = FriendsList(user=account)
                            auth_user_friend_list.save()

                        if friends.filter(pk=user.id):
                            is_friend = True
                        else:
                            is_friend = False
                        request_sent = FriendRequestStatus.NO_REQUEST_SENT.value
                        pending_friend_request_id = None

                        # CASE1: Request has been sent from THEM to YOU:
                        # FriendRequestStatus.THEM_SENT_TO_YOU
                        if get_friend_request_or_false(sender=account, reciever=user) != False:
                            request_sent = FriendRequestStatus.THEM_SENT_TO_YOU.value
                            pending_friend_request_id = get_friend_request_or_false(
                                sender=account, reciever=user
                            ).id

                        # CASE1: Request has been sent from YOU to THEM:
                        # FriendRequestStatus.YOU_SENT_TO_THEM
                        elif get_friend_request_or_false(sender=user, reciever=account) != False:
                            request_sent = FriendRequestStatus.YOU_SENT_TO_THEM.value

                        # CASE1: No Request has been sent. FriendRequestStatus.NO_REQUEST_SENT
                        else:
                            request_sent = FriendRequestStatus.NO_REQUEST_SENT.value
                            data = {
                                'pk': account.id,
                                'username': account.username,
                                'name': f'{account.first_name} {account.last_name}',
                                'pic': f'{settings.BASE_URL}{account.profile_image.url}',
                                'is_friend': is_friend,
                                'request_sent': request_sent,
                                'pending_friend_request_id': pending_friend_request_id
                            }
                            accounts.append(data
                                            )
                    payload = {
                        'msg': 'Success',
                        'data:': accounts
                    }
                    return Response(data=payload, status=status.HTTP_200_OK)
                else:
                    payload = {
                        'msg': 'no data found'
                    }
                    return Response(data=payload, status=status.HTTP_204_NO_C0NTENT)
            else:
                payload = {
                    'msg': 'This is not your request to accept'
                }
                return Response(data=payload, status=status.HTTP_204_NO_C0NTENT)
    else:
        payload = {
            'msg': 'User Not Authenticated'
        }
        return Response(data=payload, status=status.HTTP_401_UNAUTHORIZED)


'''
Cancel Friend Request API
'''


@api_view(['POST',])
@permission_classes((IsAuthenticated,))
def cancel_friend_request_api(request, *args, **kwargs):
    payload = {}
    user = request.user
    if user.is_authenticated:
        all_user = Accounts.objects.exclude(username=user)
        accounts = []
        user_id = kwargs.get("receiver_user_id")
        if user_id:
            receiver = Accounts.objects.get(pk=user_id)
            try:
                friend_requests = FriendRequest.objects.filter(
                    sender=user, reciever=receiver, is_active=True)
            except Exception as e:
                print("Nothing to cancel. Friend request deos not exist")

            # There should only be a single active friend request at any giving time.
            # Cancel them all just in case.
            if len(friend_requests) > 1:
                for request in friend_requests:
                    request.cancel()
                    for account in all_user:
                        try:
                            auth_user_friend_list = FriendsList.objects.get(
                                user=account)
                            friends = auth_user_friend_list.friends.all()
                        except FriendsList.DoesNotExist:
                            auth_user_friend_list = FriendsList(user=account)
                            auth_user_friend_list.save()

                        if friends.filter(pk=user.id):
                            is_friend = True
                        else:
                            is_friend = False
                        request_sent = FriendRequestStatus.NO_REQUEST_SENT.value
                        pending_friend_request_id = None

                        # CASE1: Request has been sent from THEM to YOU:
                        # FriendRequestStatus.THEM_SENT_TO_YOU
                        if get_friend_request_or_false(sender=account, reciever=user) != False:
                            request_sent = FriendRequestStatus.THEM_SENT_TO_YOU.value
                            pending_friend_request_id = get_friend_request_or_false(
                                sender=account, reciever=user
                            ).id

                        # CASE1: Request has been sent from YOU to THEM:
                        # FriendRequestStatus.YOU_SENT_TO_THEM
                        elif get_friend_request_or_false(sender=user, reciever=account) != False:
                            request_sent = FriendRequestStatus.YOU_SENT_TO_THEM.value

                        # CASE1: No Request has been sent. FriendRequestStatus.NO_REQUEST_SENT
                        else:
                            request_sent = FriendRequestStatus.NO_REQUEST_SENT.value
                            data = {
                                'pk': account.id,
                                'username': account.username,
                                'name': f'{account.first_name} {account.last_name}',
                                'pic': f'{settings.BASE_URL}{account.profile_image.url}',
                                'is_friend': is_friend,
                                'request_sent': request_sent,
                                'pending_friend_request_id': pending_friend_request_id
                            }
                            accounts.append(data
                                            )
                payload = {
                    'msg': 'Success',
                    'data': accounts
                }
                return Response(data=payload, status=status.HTTP_200_OK)
            else:
                # found the request. Now cancel it.
                friend_requests.first().cancel()
                for account in all_user:
                    try:
                        auth_user_friend_list = FriendsList.objects.get(
                            user=account)
                        friends = auth_user_friend_list.friends.all()
                    except FriendsList.DoesNotExist:
                        auth_user_friend_list = FriendsList(user=account)
                        auth_user_friend_list.save()

                    if friends.filter(pk=user.id):
                        is_friend = True
                    else:
                        is_friend = False
                    request_sent = FriendRequestStatus.NO_REQUEST_SENT.value
                    pending_friend_request_id = None

                    # CASE1: Request has been sent from THEM to YOU:
                    # FriendRequestStatus.THEM_SENT_TO_YOU
                    if get_friend_request_or_false(sender=account, reciever=user) != False:
                        request_sent = FriendRequestStatus.THEM_SENT_TO_YOU.value
                        pending_friend_request_id = get_friend_request_or_false(
                            sender=account, reciever=user
                        ).id

                    # CASE1: Request has been sent from YOU to THEM:
                    # FriendRequestStatus.YOU_SENT_TO_THEM
                    elif get_friend_request_or_false(sender=user, reciever=account) != False:
                        request_sent = FriendRequestStatus.YOU_SENT_TO_THEM.value

                    # CASE1: No Request has been sent. FriendRequestStatus.NO_REQUEST_SENT
                    else:
                        request_sent = FriendRequestStatus.NO_REQUEST_SENT.value
                        data = {
                            'pk': account.id,
                            'username': account.username,
                            'name': f'{account.first_name} {account.last_name}',
                            'pic': f'{settings.BASE_URL}{account.profile_image.url}',
                            'is_friend': is_friend,
                            'request_sent': request_sent,
                            'pending_friend_request_id': pending_friend_request_id
                        }
                        accounts.append(data
                                        )
                payload = {
                    'msg': 'Success',
                    'data': accounts
                }
                return Response(data=payload, status=status.HTTP_200_OK)
        else:
            payload = {
                'msg': 'Unble to cancel friend request'
            }
            return Response(data=payload, status=status.HTTP_204_NO_C0NTENT)
    else:
        payload = {
            'msg': 'User Not Authenticated'
        }
        return Response(data=payload, status=status.HTTP_401_UNAUTHORIZED)


'''
remove Friend API
'''


@api_view(['POST',])
@permission_classes((IsAuthenticated,))
def remove_friend_api(request, *args, **kwargs):
    user = request.user
    if user.is_authenticated:
        all_user = Accounts.objects.exclude(username=user)
        accounts = []
        user_id = kwargs.get("receiver_user_id")
        if user_id:
            try:
                removee = Accounts.objects.get(pk=user_id)
                friend_list = FriendsList.objects.get(user=user)
                friend_list.unfriend(removee)
                for account in all_user:
                    try:
                        auth_user_friend_list = FriendsList.objects.get(
                            user=account)
                        friends = auth_user_friend_list.friends.all()
                    except FriendsList.DoesNotExist:
                        auth_user_friend_list = FriendsList(user=account)
                        auth_user_friend_list.save()

                    if friends.filter(pk=user.id):
                        is_friend = True
                    else:
                        is_friend = False
                    request_sent = FriendRequestStatus.NO_REQUEST_SENT.value
                    pending_friend_request_id = None

                    # CASE1: Request has been sent from THEM to YOU:
                    # FriendRequestStatus.THEM_SENT_TO_YOU
                    if get_friend_request_or_false(sender=account, reciever=user) != False:
                        request_sent = FriendRequestStatus.THEM_SENT_TO_YOU.value
                        pending_friend_request_id = get_friend_request_or_false(
                            sender=account, reciever=user
                        ).id

                    # CASE1: Request has been sent from YOU to THEM:
                    # FriendRequestStatus.YOU_SENT_TO_THEM
                    elif get_friend_request_or_false(sender=user, reciever=account) != False:
                        request_sent = FriendRequestStatus.YOU_SENT_TO_THEM.value

                    # CASE1: No Request has been sent. FriendRequestStatus.NO_REQUEST_SENT
                    else:
                        request_sent = FriendRequestStatus.NO_REQUEST_SENT.value
                        data = {
                            'pk': account.id,
                            'username': account.username,
                            'name': f'{account.first_name} {account.last_name}',
                            'pic': f'{settings.BASE_URL}{account.profile_image.url}',
                            'is_friend': is_friend,
                            'request_sent': request_sent,
                            'pending_friend_request_id': pending_friend_request_id
                        }
                        accounts.append(data
                                        )
                payload = {
                    'msg': 'Success'
                }
                return Response(data=payload, status=status.HTTP_200_OK)
            except Exception as e:
                print(f"Something went wrong: {str(e)}")
        else:
            payload = {
                'msg': 'There was an error. Unable to remove that friend"'
            }
            return Response(data=payload, status=status.HTTP_204_NO_C0NTENT)
    else:
        payload = {
            'msg': 'User Not Authenticated'
        }
        return Response(data=payload, status=status.HTTP_401_UNAUTHORIZED)
