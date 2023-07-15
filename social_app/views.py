from django.shortcuts import render, redirect
from .models import Post

# Create your views here.


# @login_required
def index(request):
    context = {}
    user = request.user
    if user.is_authenticated:
        post_list = Post.objects.all().order_by('-date_post')
        context['post_list'] = post_list
    else:
        return redirect('login')
    return render(request, 'home.html', context)
