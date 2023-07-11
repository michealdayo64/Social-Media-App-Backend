from django.urls import path
from .views import message_index

urlpatterns = [
    path('', message_index, name="message-index")
]
