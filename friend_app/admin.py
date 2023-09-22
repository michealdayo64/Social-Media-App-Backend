from django.contrib import admin
from .models import FriendsList, FriendRequest
# Register your models here.

admin.site.register([FriendsList, FriendRequest])
