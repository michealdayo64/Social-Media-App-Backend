from rest_framework import serializers  # type: ignore
from .models import Accounts


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Accounts
        fields = ('username', 'email', 'first_name', 'last_name', 'password', )
        extra_kwargs = {'password': {'write_only': True}}


class LoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = Accounts
        fields = ('email', 'password', )
