from django.urls import path
from .views import private_chat_room_view

urlpatterns = [
    path('', private_chat_room_view, name="message-index")
]
