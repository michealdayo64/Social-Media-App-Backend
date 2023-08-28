from django.contrib import admin
from .models import GroupChatRoom
# from django.core.paginator import Paginator
# from django.core.cache import cache
# from django.db import models
# Register your models here.


class GroupChatRoomAdmin(admin.ModelAdmin):
    list_display = ['id', 'title']
    search_fields = ['id', 'title']
    list_display = ['id',]

    class Meta:
        Model = GroupChatRoom


admin.site.register(GroupChatRoom, GroupChatRoomAdmin)
