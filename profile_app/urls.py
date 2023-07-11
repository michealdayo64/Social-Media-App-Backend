from django.urls import path
from .views import profile_index

urlpatterns = [
    path('', profile_index, name="profile-index")
]
