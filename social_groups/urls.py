from django.urls import path
from .views import group_list, group_detail, getToken, roomCall, createMember


urlpatterns = [
    path('', group_list, name='group-list'),
    path('group-detail/<id>/', group_detail, name='group-detail'),
    path('get-token/', getToken, name="get-token"),
    path('room/', roomCall, name='room-call'),
    path('create-member/', createMember, name='create-member')
]
