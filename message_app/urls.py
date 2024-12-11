from django.urls import path
from .views import private_chat_room_view, create_or_return_private_chat, getFriendsChatList, createOrReturnPrivateChatApi

urlpatterns = [
    path('', private_chat_room_view, name="private-chat-room"),
    path('create-or-return-private-chat/<user2_id>/', create_or_return_private_chat,
         name="create-or-return-private-chat"),


    # API
    path('get-friends-chat-list/', getFriendsChatList),
    path('create-or-return-private-chat-api/<user2_id>/',
         createOrReturnPrivateChatApi)
]
