from django.urls import path
from .views import index, postList, like_post
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path('home/', index, name="index"),
    path('post-list/', postList, name='post-list'),
    path('like-post/<id>/', csrf_exempt(like_post), name='like-post')
]
