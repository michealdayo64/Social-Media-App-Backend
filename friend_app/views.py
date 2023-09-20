from django.shortcuts import render
from friend_app.models import FriendsList
from account.models import Accounts

# Create your views here.

'''
All User
'''
def friend_index(request):
    user_id = request.user.id
    all_user = Accounts.objects.exclude(id = user_id)
    for i in all_user:
        user = FriendsList.objects.get(id = user_id) 
        #if not i.username in 
    print(all_user)
    context = {
        'all_user': all_user
    }
    return render(request, 'friend_app/friend.html', context)
