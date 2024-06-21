from django.urls import path
from .views import (friend_index, send_friend_request, accept_friend_request, decline_friend_request,
                    cancel_friend_request, remove_friend, friend_detail, total_num_friends_api, total_num_friend_request_api,
                    get_all_user_api, send_friend_request_api, accept_friend_request_api, decline_friend_request_api, cancel_friend_request_api, remove_friend_api)

urlpatterns = [

    # ................................................ URL .............................................................
    path('', friend_index, name='friend-index'),
    path('send-friend-request/<user_id>/',
         send_friend_request, name='send-friend-request'),
    path('accept-friend-request/<pending_friend_id>/',
         accept_friend_request, name="accept-friend-request"),
    path('decline-friend-request/<pending_friend_id>/',
         decline_friend_request, name="decline-friend-request"),
    path('cancel_friend_request/<receiver_user_id>/',
         cancel_friend_request, name="cancel_friend_request"),
    path('remove_friend/<receiver_user_id>/',
         remove_friend, name="remove_friend"),
    path('friend-detail/<user_id>/', friend_detail, name="friend-detail"),




    # --------------------------------------------- API URL ------------------------------------------------
    path('friend_count/', total_num_friends_api, name='friend-count'),
    path('total_friend_request/', total_num_friend_request_api,
         name='total-friend-request'),
    path('get_all_user/', get_all_user_api, name='get-all-user'),
    path('send-friend-request-api/<user_id>/', send_friend_request_api),
    path('accept-friend-request-api/<pending_friend_id>/',
         accept_friend_request_api),
    path('decline-friend-request-api/<pending_friend_id>/',
         decline_friend_request_api),
    path('cancel-friend-request-api/<receiver_user_id>/',
         cancel_friend_request_api),
    path('remove-friend-api/<receiver_user_id>/', remove_friend_api)
]
