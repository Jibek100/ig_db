from django.http import HttpResponse
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Profile, Post, Comment, Reply
from .serializers import profileSerializer, postSerializer, commentSerializer, replySerializer

def home(request):
    html = "<html><body>This is the site's homepage. </body></html>"
    return HttpResponse(html)

@api_view(['GET', 'POST'])
def profile(request):
    if request.method == 'GET':
        profiles = Profile.objects.all()
        serializer = profileSerializer(profiles, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = profileSerializer(data=request.data, many=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'DELETE'])
def profileData(request, pk):
    try:
        profile = Profile.objects.get(pk=pk)
    except profile.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = profileSerializer(profile)
        return Response(serializer.data)

    elif request.method == 'DELETE':
        profile.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET', 'POST'])
def post(request):
    if request.method == 'GET':
        posts = Post.objects.all()
        serializer = postSerializer(posts, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = postSerializer(data=request.data, many=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'DELETE'])
def postData(request, pk):
    try:
        post = Post.objects.get(pk=pk)
    except post.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = postSerializer(profile)
        return Response(serializer.data)

    elif request.method == 'DELETE':
        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET', 'POST'])
def comment(request):
    if request.method == 'GET':
        comments = Comment.objects.all()
        serializer = commentSerializer(comments, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = commentSerializer(data=request.data, many=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'DELETE'])
def commentData(request, pk):
    try:
        comment = Comment.objects.get(pk=pk)
    except comment.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = commentSerializer(comment)
        return Response(serializer.data)

    elif request.method == 'DELETE':
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET', 'POST'])
def reply(request):
    if request.method == 'GET':
        replies = Reply.objects.all()
        serializer = replySerializer(replies, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = replySerializer(data=request.data, many=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'DELETE'])
def replyData(request, pk):
    try:
        reply = Reply.objects.get(pk=pk)
    except reply.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = replySerializer(reply)
        return Response(serializer.data)

    elif request.method == 'DELETE':
        reply.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

