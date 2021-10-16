from rest_framework import serializers
from .models import Profile, Post, Comment, Reply

class profileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['profile_id', 'username', 'bio', 'type', 'user']

class postSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['post_id', 'text', 'date_posted', 'profile', 'like_count', 'comment_count', 'engament', 'impression', 'reach', 'saved']
