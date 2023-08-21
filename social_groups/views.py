from django.shortcuts import render
from django.conf import settings

# Create your views here.

def group_list(request):

    return render(request, 'group_list.html')

def group_detail(request):
    room_id = 1
    context = {
        'room_id': room_id,
        'debug_mode': settings.DEBUG
    }
    return render(request, 'group_detail.html', context)
