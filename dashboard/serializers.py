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
    comment_id = serializers.PrimaryKeyRelatedField(queryset=Comment.objects.all(), required=False)
    class Meta:
        model = Reply
        fields = '__all__'

class commentSerializer(WritableNestedModelSerializer):
    replies = replySerializer(many=True)
    class Meta:
        model = Comment
        fields = '__all__'

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
        for reply in replies_data:
            Reply.objects.create(comment_id=comment, **reply)
        return comment

    def update(self, instance, validated_data):
        post = validated_data.get('post_id')
        ts = post.ts
        replies_data = validated_data.pop('replies')
        for reply in replies_data:
            reply_id = reply.get('id', None)
            if not reply_id:
                reply = Reply.objects.create(comment_id=instance, **reply)
        return instance


