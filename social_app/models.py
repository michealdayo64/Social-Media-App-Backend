from django.db import models
from django.conf import settings
from message_app.utils import calculate_timestamp

# Create your models here.


def get_post_image_filepath(self, filename):
    pic = f'post_images/{self.user.pk}/{"post_image_"}{self.id}/'
    if pic.endswith(".png"):
        return pic
    elif pic.endswith(".MP4"):
        return pic


class Post(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name='author')
    user_post = models.TextField(null=True, blank=True)
    file = models.FileField(
        upload_to="post_images/", null=True, blank=True)
    date_post = models.DateTimeField(auto_now_add=True)
    date_post_update = models.DateTimeField(auto_now=True)
    user_like_post = models.ManyToManyField(
        settings.AUTH_USER_MODEL, blank=True)
    reposted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name='reposted_by')
    repost_users = models.ManyToManyField(
        settings.AUTH_USER_MODEL, blank=True, related_name="users_repost")

    def __str__(self):
        return f"Post By {self.user.username}"
    
    @property
    def date_format(self):
        if self.date_post:
            return calculate_timestamp(self.date_post)


class Comment(models.Model):
    user = user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name='commenter')
    post_id = models.ForeignKey(
        Post, on_delete=models.CASCADE, blank=True, null=True, related_name='comments')
    comment = models.TextField(null=True, blank=True)
    date_comment = models.DateTimeField(auto_now_add=True)
    date_comment_update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Post Commented by {self.comment}'
