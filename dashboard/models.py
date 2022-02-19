from django.db import models
from django.utils import timezone
from django.conf import settings

class Profile(models.Model):
    id = models.CharField(primary_key=True, max_length=100)
    username = models.CharField(max_length=20)
    bio = models.TextField(max_length=150)
    type = models.BooleanField()

class Post(models.Model):
    id = models.CharField(primary_key=True, max_length=100)
    text = models.TextField()
    date_posted = models.DateTimeField(default=timezone.now)
    profile_id = models.ForeignKey(Profile, on_delete=models.CASCADE)
    like_count = models.IntegerField()
    comment_count = models.IntegerField()
    engagement = models.IntegerField(null=True, blank=True)
    impression = models.IntegerField(null=True, blank=True)
    reach = models.IntegerField(null=True, blank=True)
    saved = models.IntegerField(null=True, blank=True)
    ts = models.DateTimeField(default=timezone.now, null=True, blank=True)

class Comment(models.Model):
    id = models.CharField(primary_key=True, max_length=100)
    text = models.TextField()
    date_posted = models.DateTimeField(default=timezone.now)
    username = models.CharField(max_length=20)
    post_id = models.ForeignKey(Post, on_delete=models.CASCADE)
    like_count = models.IntegerField()
    obscene = models.DecimalField(max_digits=21, decimal_places=20, null=True, blank=True)
    insult = models.DecimalField(max_digits=21, decimal_places=20, null=True, blank=True)
    toxic = models.DecimalField(max_digits=21, decimal_places=20, null=True, blank=True)
    severe_toxic = models.DecimalField(max_digits=21, decimal_places=20, null=True, blank=True)
    identity_hate = models.DecimalField(max_digits=21, decimal_places=20, null=True, blank=True)
    threat = models.DecimalField(max_digits=21, decimal_places=20, null=True, blank=True)

class Reply(models.Model):
    id = models.CharField(primary_key=True, max_length=100)
    text = models.TextField()
    date_posted = models.DateTimeField(default=timezone.now)
    username = models.CharField(max_length=20)
    post_id = models.ForeignKey(Post, on_delete=models.CASCADE)
    like_count = models.IntegerField()
    comment_id = models.ForeignKey(Comment, related_name='replies', on_delete=models.CASCADE)
    obscene = models.DecimalField(max_digits=21, decimal_places=20, null=True, blank=True)
    insult = models.DecimalField(max_digits=21, decimal_places=20, null=True, blank=True)
    toxic = models.DecimalField(max_digits=21, decimal_places=20, null=True, blank=True)
    severe_toxic = models.DecimalField(max_digits=21, decimal_places=20, null=True, blank=True)
    identity_hate = models.DecimalField(max_digits=21, decimal_places=20, null=True, blank=True)
    threat = models.DecimalField(max_digits=21, decimal_places=20, null=True, blank=True)

