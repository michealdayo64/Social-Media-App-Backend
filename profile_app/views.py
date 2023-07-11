from django.shortcuts import render

# Create your views here.


def profile_index(request):
    return render(request, 'profile_app/profile.html')
