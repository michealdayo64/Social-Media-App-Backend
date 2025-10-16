from rest_framework import serializers
from .models import RoomChatMessage


class RoomChatMessageSerializer(serializers.ModelSerializer):

    class Meta:
        model = RoomChatMessage
        fields = ('id', 'content', )
