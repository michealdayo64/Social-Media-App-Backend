from django.urls import path
from .views import (index, postList, like_post, get_like_count, user_comment, post_detail, get_post_comments,
                    comment_count, create_post, userSharePost, index_api, comment_api, user_like_post_api, userRepostApi, search_post)
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path('', index, name="index"),
    path('search-post/', search_post, name='search'),
    path('post-list/', postList, name='post-list'),
    path('like-post/<id>/', csrf_exempt(like_post), name='like-post'),
    path('get-like-count/<id>/', get_like_count, name="get-like-count"),
    path('user-comment/<id>/', csrf_exempt(user_comment), name='user-comment'),
    path('comment-count/<id>/', comment_count, name='comment-count1'),
    path('create-post/', (create_post), name='create-post'),
    path('user-share-post/<id>/', userSharePost, name='user-share-post'),
    path('post-detail/<id>/', post_detail, name='post-detail'),
    path('get-post-comments/<id>/', get_post_comments, name='get-post-comment'),


    # .................... API URL ................................
    path('index-api/', index_api),
    path('comment-api/<id>/', comment_api),
    path('user-like-post-api/<id>/', user_like_post_api),
    path('repost-api/<id>/', userRepostApi)
]
