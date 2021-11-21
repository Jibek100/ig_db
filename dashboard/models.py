from django.db import models
from django.utils import timezone
from django.conf import settings

class Profile(models.Model):
    profile_id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=20)
    bio = models.TextField(max_length=150)
    type = models.BooleanField()

class Post(models.Model):
    post_id = models.IntegerField(primary_key=True)
    text = models.TextField()
    date_posted = models.DateTimeField(default=timezone.now)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    like_count = models.IntegerField()
    comment_count = models.IntegerField()
    engament = models.IntegerField(null=True, blank=True)
    impression = models.IntegerField(null=True, blank=True)
    reach = models.IntegerField(null=True, blank=True)
    saved = models.IntegerField(null=True, blank=True)

class Comment(models.Model):
    comment_id = models.IntegerField(primary_key=True)
    text = models.TextField()
    date_posted = models.DateTimeField(default=timezone.now)
    username = models.CharField(max_length=20)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    is_reply = models.BooleanField()
    like_count = models.IntegerField(null=True, blank=True)
    parent_comment_id = models.IntegerField(null=True, blank=True)
    obscene = models.DecimalField(max_digits=21, decimal_places=20, null=True, blank=True)
    insult = models.DecimalField(max_digits=21, decimal_places=20, null=True, blank=True)
    toxic = models.DecimalField(max_digits=21, decimal_places=20, null=True, blank=True)
    severe_toxic = models.DecimalField(max_digits=21, decimal_places=20, null=True, blank=True)
    identity_hate = models.DecimalField(max_digits=21, decimal_places=20, null=True, blank=True)
    threat = models.DecimalField(max_digits=21, decimal_places=20, null=True, blank=True)


