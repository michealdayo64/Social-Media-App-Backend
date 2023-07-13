from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

# Create your views here.


# @login_required
def index(request):
    user = request.user
    if user.is_authenticated:
        print("Home")
    else:
        return redirect('login')
    return render(request, 'home.html')
