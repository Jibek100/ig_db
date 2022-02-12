from collections import OrderedDict
from rest_framework import serializers
from drf_writable_nested.serializers import WritableNestedModelSerializer
from .models import *
from .views import *

class profileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = '__all__'

class postSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = '__all__'

    def create(self, validated_data):
        ts = validated_data.get('date_posted')
        post = Post.objects.create(**validated_data, ts=ts)
        return post

class replySerializer(serializers.ModelSerializer):
    class Meta:
        model = Reply
        fields = '__all__'

class commentSerializer(WritableNestedModelSerializer):
    replies = replySerializer(many=True)
    class Meta:
        model = Comment
        fields = ['id', 'text', 'date_posted', 'username',
                  'post_id', 'like_count', 'replies', 'obscene', 'insult',
                  'toxic', 'severe_toxic', 'identity_hate', 'threat']

    def update(self, instance, validated_data):
        post = validated_data.get('post_id')
        ts = post.ts
        replies_data = validated_data.pop('replies')
        for reply_data in replies_data:
            if not Reply.objects.filter(id=reply_data['id']).exists():
                reply = Reply.objects.create(comment=instance, **reply_data)
        return instance

    def create(self, validated_data):
        post = validated_data.get('post_id')
        ts = post.ts

        replies_data = validated_data.pop('replies')
        comment = Comment.objects.create(**validated_data)
        if validated_data.get('date_posted') <= ts:
            comment.delete()
        else:
            post.ts = validated_data.get('date_posted')
            post.save()
        for reply_data in replies_data:
            Reply.objects.create(comment=comment, **reply_data)
        return comment


