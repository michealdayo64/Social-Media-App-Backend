from django.contrib import admin
from .models import PrivateChatRoom


class PrivateChatRoomAdmin(admin.ModelAdmin):
    list_display = ['id', 'user1', 'user2']
    search_fields = ['id', 'user1__username', 'user2__username', 'user1__email', 'user2__email']
    list_display = ['id',]

    class Meta:
        Model = PrivateChatRoom

admin.site.register(PrivateChatRoom, PrivateChatRoomAdmin)