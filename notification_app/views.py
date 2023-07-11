from django.shortcuts import render

# Create your views here.


def notification_index(request):
    return render(request, 'notification_app/notification.html')
