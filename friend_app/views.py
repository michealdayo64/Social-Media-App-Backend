from django.shortcuts import render

# Create your views here.


def friend_index(request):
    return render(request, 'friend_app/friend.html')
