from django.urls import path
from .views import group_list


urlpatterns = [
    path('', group_list, name = 'group-list')
]