from django.db import models
from account.models import Account

# Create your models here.


class Post(models.Model):
    user = models.ForeignKey(
        Account, on_delete=models.CASCADE, null=True, blank=True, related_name='author')
    user_post = models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to='media/', null=True, blank=True)
    date_post = models.DateTimeField(auto_now_add=True)
    date_post_update = models.DateTimeField(auto_now=True)
    user_like_post = models.ManyToManyField(Account, blank=True)

    def __str__(self):
        return f"Post By {self.user}"
