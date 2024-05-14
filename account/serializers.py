from rest_framework import serializers # type: ignore
from .models import Accounts


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Accounts
        fields = ('username', 'email', 'password')
