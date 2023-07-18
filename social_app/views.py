from django.shortcuts import render, redirect
from .models import Post
import json
from django.http import JsonResponse

# Create your views here.


def index(request):
    context = {}
    user = request.user
    if user.is_authenticated:
        post_list = Post.objects.all().order_by('-date_post')
        context['post_list'] = post_list
    else:
        return redirect('login')
    return render(request, 'home.html', context)


'''
All Users Post
'''


def postList(request):
    payload = {}
    p_list = []
    user = request.user
    if user.is_authenticated:
        post_list = Post.objects.all().order_by('-date_post')
        for i in post_list:
            payload['user'] = i.user.username
            payload['user_post'] = i.user_post
            payload['image'] = i.image.url
            payload['date_post'] = i.date_post
            p_list.append(payload)
    else:
        payload['response'] = 'User not authenticated'
    return JsonResponse(json.dumps(payload), content_type="application/json")


def like_post(request, id):
    payload = {}
    user = request.user
    if user.is_authenticated:
        post_id = Post.objects.get(id=id)
        if user in post_id.user_like_post.all():
            post_id.user_like_post.remove(user)
            payload['response'] = 'Unlike User'
        else:
            post_id.user_like_post.add(user)
            payload['response'] = 'Like User'

    else:
        payload['response'] = 'User Needs to be authenticated'
    return JsonResponse(payload, content_type="application/json", safe=False)
