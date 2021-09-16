from django.db import models
from django.utils import timezone

class Profile(models.Model):
    username = models.CharField(max_length=100, primary_key=True)
    bio = models.TextField()
    type = models.TextField()

class Post(models.Model):
    post_id = models.IntegerField(primary_key=True)
    text = models.TextField()
    date_posted = models.DateTimeField(default=timezone.now)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    like_count = models.IntegerField()
    comment_count = models.IntegerField()
    engament = models.IntegerField()
    impression = models.IntegerField()
    reach = models.IntegerField()
    saved = models.IntegerField()

class Comment(models.Model):
    comment_id = models.IntegerField(primary_key=True)
    content = models.TextField()
    date_posted = models.DateTimeField(default=timezone.now)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    like_count = models.IntegerField()

class Reply(models.Model):
    reply_id = models.IntegerField(primary_key=True)
    content = models.TextField()
    date_posted = models.DateTimeField(default=timezone.now)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
    like_count = models.IntegerField()
