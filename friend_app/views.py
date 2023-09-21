from django.shortcuts import render
from friend_app.models import FriendsList
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
            accounts.append(
                (account, auth_user_friend_list.is_mutual_friend(account)))
        print(accounts)
        context = {
            'accounts': accounts
        }
        return render(request, 'friend_app/friend.html', context)
    else:
        print("User not authenticated")
    return render(request, 'friend_app/friend.html', context)
