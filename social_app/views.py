# type: ignore
from rest_framework.decorators import api_view, permission_classes  # type: ignore
from rest_framework.permissions import IsAuthenticated, AllowAny  # type: ignore
from rest_framework import status  # type: ignore
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response  # type: ignore
from .serializers import PostSerializer, CommentSerializer
from datetime import datetime
from django.shortcuts import render, redirect
from .models import Post, Comment
from account.models import Accounts
from account.serializers import UserSerializer
from friend_app.models import FriendsList
import json
from django.http import JsonResponse
# import os
from django.conf import settings
# from django.core.files.storage import FileSystemStorage
import base64
from django.core import files
from django.core.files.base import ContentFile
import random

# Create your views here.


# TEMP_PROFILE_IMAGE_NAME = "temp_profile_image.png"


'''
All Users Post
'''


def index(request):
    context = {}
    user = request.user
    if user.is_authenticated:
        friend = FriendsList.objects.get(user=user)
        friends_list = friend.friends.all()

        '''
        List of post according to User friend
        '''
        '''post_list = list(Post.objects.filter(user__in=list(
            friends_list) + [user,]).order_by('-date_post'))'''
        post_list = list(Post.objects.all())
        random.shuffle(post_list)
        context['post_list'] = post_list
    else:
        return redirect('login')
    return render(request, 'home.html', context)


def search_post(request):
    context = {}
    user = request.user
    if user.is_authenticated:
        input_search = request.GET.get("q")
        friend = FriendsList.objects.get(user=user)
        friends_list = friend.friends.all()
        if len(input_search) > 0:
            post_list = Post.objects.filter(user_post__icontains = input_search).distinct()
            context["post_list"] = post_list
        else:
            print("No Input")
    else:
        return redirect('login')
    return render(request, 'search.html', context)
        


'''
All Users Post with Json
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


'''
Image from base 64 Encoding
'''


def save_post_image_form_base64String(imageString):
    format, imgstr = imageString.split(';base64,')
    ext = format.split('/')[-1]
    img = base64.b64decode(imgstr)
    file_data = ContentFile(img)
    file_name = "'myphoto." + ext
    return file_name, file_data


'''
Create a post with json
'''


def create_post(request):
    payload = {}
    user = request.user
    if user.is_authenticated:
        ns = json.loads(request.body)
        inputPostValue = ns.get('inputPostValue')
        imgPostValue = ns.get('imgPostValue')

        if inputPostValue and imgPostValue:
            post = Post.objects.create(
                user=user, user_post=inputPostValue)
            print(post)
            file_name, file_data = save_post_image_form_base64String(
                imgPostValue)
            # print(post.file.save(file_name, file_data))
            post.file.save(file_name, file_data)
            payload['response'] = 'Post created Successfully'
        else:
            if inputPostValue:
                post = Post.objects.create(
                    user=user, user_post=inputPostValue)
                print(post)
                payload['response'] = 'Post created Successfully'
            else:
                post = Post.objects.create(
                    user=user)
                print(post)
                file_name, file_data = save_post_image_form_base64String(
                    imgPostValue)
                # print(post.image.save(file_name, file_data))
                post.file.save(file_name, file_data)
                payload['response'] = 'Post created Successfully'

    else:
        payload['response'] = 'User has to be authenticated'
    return JsonResponse(json.dumps(payload), content_type="application/json", safe=False)


'''
User like post with Json
'''


def like_post(request, id):
    payload = {}
    user = request.user
    if user.is_authenticated:
        post_id = Post.objects.get(id=id)
        if user in post_id.user_like_post.all():
            post_id.user_like_post.remove(user)
            like_count = post_id.user_like_post.all().count()
            payload['response'] = 'Unlike User'
            payload['like_count'] = like_count
        else:
            post_id.user_like_post.add(user)
            like_count = post_id.user_like_post.all().count()
            payload['response'] = 'Like User'
            payload['like_count'] = like_count

    else:
        payload['response'] = 'User Needs to be authenticated'
    return JsonResponse(payload, content_type="application/json", safe=False)


'''
Get like count for each post with json
'''


def get_like_count(request, id):
    payload = {}
    user = request.user
    if user.is_authenticated:
        post_id = Post.objects.get(id=id)
        like_count = post_id.user_like_post.all().count()
        payload['response'] = 'Unlike User'
        payload['like_count'] = like_count

    else:
        payload['response'] = 'User Needs to be authenticated'
    return JsonResponse(payload, content_type="application/json", safe=False)


'''
User comment on post with Json
'''


def user_comment(request, id):
    payload = {}
    comment_list = []
    user = request.user
    if user.is_authenticated:
        post_id = Post.objects.get(id=id)
        ns = json.loads(request.body)
        inputValue = ns['inputValue']
        if request.method == 'POST':
            comment = Comment.objects.create(
                user=user, post_id=post_id, comment=inputValue)
            payload['response'] = 'Comment Successful'

            all_comment_list = Comment.objects.filter(post_id=post_id)
            if all_comment_list:
                for i in all_comment_list:
                    comment_list.append({
                        'user': i.user.username,
                        'comment': i.comment
                    })
                str_time = datetime.strftime(comment.date_comment, "%I:%M %p")
                str_time = str_time.strip("0")
                payload['comment_list'] = comment_list
                payload['comment_count'] = len(comment_list)
                payload['user'] = user.username
                payload['comment'] = comment.comment
                payload['date'] = str_time

            else:
                payload['response'] = 'No Input value'
    else:
        payload['response'] = 'User has to be Authenticated'

    return JsonResponse((payload), content_type="application/json", safe=False)


def post_detail(request, id):
    user = request.user
    if user.is_authenticated:
        #get_post_id = kwargs.get('id')
        post_id = Post.objects.get(id = id)
        comment_list = Comment.objects.filter(post_id = post_id)
        if request.method == 'POST':
            comment_input = request.POST.get('comment_input')
            if len(comment_input > 0):
                comment = Comment.objects.create(user = user, post_id = post_id, comment = comment_input)
                return redirect('post-detail', post_id)
    context = {
        'comment_list': comment_list,
        'post_id': post_id
    }
    return render(request, 'post-detail.html', context)


'''
Comment Count for each post
'''


def comment_count(request, id):
    payload = {}
    user = request.user
    if user.is_authenticated:
        post_id = Post.objects.get(id=id)
        va = Comment.objects.filter(post_id=post_id).count()
        payload['response'] = va

    return JsonResponse(payload, content_type="application/json", safe=False)


''' 
User Share Post
'''


def userSharePost(request, id):
    user = request.user
    post_id = Post.objects.get(id=id)
    user_post = post_id.user_post
    image = post_id.file
    posted_by = post_id.user
    Post.objects.create(user=user, user_post=user_post,
                        file=image, reposted_by=posted_by)
    return redirect('index')


@api_view(['GET',])
@permission_classes((IsAuthenticated,))
def index_api(request):
    payload = {}
    user = request.user
    if user.is_authenticated:
        friend = FriendsList.objects.get(user=user)
        friends_list = friend.friends.all()

        me = Accounts.objects.get(pk=user.id)
        '''
        List of post according to User friend
        '''
        post_list = Post.objects.filter(user__in=list(
            friends_list) + [user,]).order_by('-date_post')

        user_serializer = UserSerializer(me, many=False)
        print(user_serializer.data)

        serializer = PostSerializer(
            post_list, many=True, context={'request': request})
        payload = {
            'user': user_serializer.data,
            'msg': 'Success',
            'post_list': serializer.data,

        }
        return Response(data=payload, status=status.HTTP_200_OK)
    else:
        payload = {
            'msg': 'User not Authenticated'
        }
        return Response(data=payload, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET',])
@permission_classes((IsAuthenticated,))
def comment_api(request, id):
    payload = {}
    user = request.user
    if user.is_authenticated:
        post_id = Post.objects.get(id=id)
        comment_list = Comment.objects.filter(post_id=post_id)
        serializer = CommentSerializer(comment_list, many=True)
        print(serializer.data)
        aa = []
        payload = {
            'msg': 'Success',
            'comment_list': serializer.data
        }
        aa.append(payload)

        return Response(data=aa, status=status.HTTP_200_OK)
    else:
        payload = {
            'msg': "User not Authorized"
        }
        return Response(data=payload, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST',])
@permission_classes((IsAuthenticated,))
def user_like_post_api(request, id):
    payload = {}
    user = request.user
    if user.is_authenticated:
        post_id = Post.objects.get(id=id)
        if user in post_id.user_like_post.all():
            post_id.user_like_post.remove(user)
            # like_count = post_id.user_like_post.all().count()
            serializer = PostSerializer(instance=post_id, many=False)
            payload['msg'] = 'Success'
            payload['like_count'] = serializer.data
            return Response(data=payload, status=status.HTTP_200_OK)
        else:
            post_id.user_like_post.add(user)
            # like_count = post_id.user_like_post.all().count()
            serializer = PostSerializer(instance=post_id, many=False)
            payload['msg'] = 'Success'
            payload['like_count'] = serializer.data
            return Response(data=payload, status=status.HTTP_200_OK)

    else:
        payload['response'] = 'User Needs to be authenticated'
        return Response(data=payload, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST',])
@permission_classes((IsAuthenticated,))
def userRepostApi(request, id):
    payload = {}
    user = request.user
    post_id = Post.objects.get(id=id)
    user_post = post_id.user_post
    if (post_id.file):
        image = post_id.file
        posted_by = post_id.user

        print("okkkk----ok")
        if user in post_id.repost_users.all():
            payload = {
                'msg': "Post has been reposted already",
            }
            return Response(data=payload, status=status.HTTP_200_OK)
        else:
            post_id.repost_users.add(user)
            post = Post.objects.create(user=posted_by, user_post=user_post,
                                       file=image, reposted_by=user)
            post.repost_users.add(user)
            serializer = PostSerializer(post, many=False)
            payload = {
                'msg': "Success",
                'post': serializer.data
            }
            return Response(data=payload, status=status.HTTP_200_OK)
    else:
        posted_by = post_id.user
        if user in post_id.repost_users.all():
            payload = {
                'msg': "Post has been reposted already",
            }
            return Response(data=payload, status=status.HTTP_200_OK)
        else:
            post_id.repost_users.add(user)
            post = Post.objects.create(user=posted_by, user_post=user_post,
                                       reposted_by=user)
            post.repost_users.add(user)
            serializer = PostSerializer(post, many=False)
            payload = {
                'msg': "Success",
                'post': serializer.data
            }
            return Response(data=payload, status=status.HTTP_200_OK)
