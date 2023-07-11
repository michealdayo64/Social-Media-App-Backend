from django.urls import path
from .views import friend_index

urlpatterns = [
    path('', friend_index, name='friend-index')
]
