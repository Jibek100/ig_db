from rest_framework import serializers
from .models import Profile, Post, Comment

class profileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['profile_id', 'username', 'bio', 'type']

class postSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['post_id', 'text', 'date_posted', 'profile', 'like_count', 'comment_count', 'engament', 'impression', 'reach', 'saved']

class commentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['comment_id', 'text', 'date_posted', 'username', 'post', 'like_count', 'parent_comment_id', 'is_reply', 'obscene', 'insult', 'toxic', 'severe_toxic', 'identity_hate', 'threat']
