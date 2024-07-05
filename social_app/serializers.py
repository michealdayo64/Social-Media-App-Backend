from rest_framework import serializers  # type: ignore
from account.models import Accounts
from .models import Post, Comment
from account.serializers import UserSerializer


class PostSerializer(serializers.ModelSerializer):
    user = UserSerializer(many=False)
    user_like_post = UserSerializer(many=True)
    comments = serializers.StringRelatedField(many=True)

    class Meta:
        model = Post
        fields = ('pk', 'user', 'user_post', 'comments', 'file', 'date_post',
                  'date_post_update', 'user_like_post', 'posted_by', )


class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(many=False)
    post_id = PostSerializer(many=False)

    class Meta:
        model = Comment
        fields = ('pk', 'user', 'post_id', 'comment',
                  'date_comment', 'date_comment_update', )
