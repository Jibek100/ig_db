from rest_framework import serializers
from drf_writable_nested.serializers import WritableNestedModelSerializer
from .models import Profile, Post, Comment, Reply

class profileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['profile_id', 'username', 'bio', 'type']

class postSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['post_id', 'text', 'date_posted', 'profile', 'like_count',
                  'comment_count', 'engament', 'impression', 'reach', 'saved']

class replySerializer(serializers.ModelSerializer):
    class Meta:
        model = Reply
        fields = ['reply_id', 'text', 'date_posted']

class commentSerializer(WritableNestedModelSerializer):
    replies = replySerializer(many=True)
    class Meta:
        model = Comment
        fields = ['comment_id', 'text', 'date_posted', 'username',
                  'post', 'like_count', 'replies', 'obscene', 'insult',
                  'toxic', 'severe_toxic', 'identity_hate', 'threat']

    def create(self, validated_data):
        replies_data = validated_data.pop('replies')
        comment = Comment.objects.create(**validated_data)
        for reply_data in replies_data:
            Reply.objects.create(comment=comment, **reply_data)
        return comment

