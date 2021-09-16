from django.db import models
from django.utils import timezone

class Profile(models.Model):
    username = models.CharField(max_length=100)
    bio = models.TextField()
    type = models.TextField()

class Post(models.Model):
    text = models.TextField()
    date_posted = models.DateTimeField(default=timezone.now)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    like_count = models.IntegerField()

class Comment(models.Model):
    content = models.TextField()
    date_posted = models.DateTimeField(default=timezone.now)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    like_count = models.IntegerField()

class Reply(models.Model):
    content = models.TextField()
    date_posted = models.DateTimeField(default=timezone.now)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
    like_count = models.IntegerField()
