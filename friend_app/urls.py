from django.urls import path
from .views import friend_index, send_friend_request

urlpatterns = [
    path('', friend_index, name='friend-index'),
    path('send-friend-request/<user_id>/',
         send_friend_request, name='send-friend-request')
]
