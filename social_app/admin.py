from django.contrib import admin
from .models import Post, Comment, sharedPost

# Register your models here.

admin.site.register([Post, Comment, sharedPost])
