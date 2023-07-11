from django.shortcuts import render

# Create your views here.


def message_index(request):
    return render(request, 'message_app/message.html')
