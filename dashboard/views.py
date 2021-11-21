import pandas as pd
import joblib
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse
from rest_framework import status
from .engine import SearchEngine
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Profile, Post, Comment
from .serializers import profileSerializer, postSerializer, commentSerializer
_MODEL_TYPE_NAMES = ['obscene', 'insult', 'toxic', 'severe_toxic', 'identity_hate', 'threat']


def home(request):
    html = "<html><body>This is the site's homepage. </body></html>"
    return HttpResponse(html)

def getCommentsDf(fields = ['comment_id', 'text', 'username', 'like_count', 'post']):
    comments = Comment.objects.all()
    serializer = commentSerializer(comments, many=True)
    # data = [{}] * len(serializer.data)
    # print(len(serializer.data))
    # for idx, dataInstance in enumerate(serializer.data):
    #     print(dataInstance)
    return pd.DataFrame(serializer.data)

@api_view(['GET'])
def searchComment(request):
    text, engine = request.data['text'], None
    engine = SearchEngine(target='text')
    engine.importDf(getCommentsDf())
    engine.buildIndex()
    return Response(engine.searchQuery(text))

@api_view(['GET'])
def classifyComment(request, pk):
    commentText = Comment.objects.get(pk=pk).text
    models = {modelName:joblib.load('dashboard/models/' + modelName + '.pkl') for modelName in _MODEL_TYPE_NAMES}
    vectorizer = joblib.load('dashboard/models/' + 'vectorizer' + '.pkl')
    output = {modelName:models[modelName].predict_proba(vectorizer.transform([commentText])) for modelName in models}
    return Response(output)

@api_view(['GET'])
def classifyComments(request):
    comments = Comment.objects.all()
    list = []
    for comment in comments:
        commentText = comment.text
        models = {modelName:joblib.load('dashboard/models/' + modelName + '.pkl') for modelName in _MODEL_TYPE_NAMES}
        vectorizer = joblib.load('dashboard/models/' + 'vectorizer' + '.pkl')
        output = {modelName:models[modelName].predict_proba(vectorizer.transform([commentText])) for modelName in models}
        list.append(output)
    return Response(list)

def classifyCommentsBy():
    comments = Comment.objects.all()
    list = []
    for comment in comments:
        commentText = comment.text
        models = {modelName:joblib.load('dashboard/models/' + modelName + '.pkl') for modelName in _MODEL_TYPE_NAMES}
        vectorizer = joblib.load('dashboard/models/' + 'vectorizer' + '.pkl')
        output = {modelName:models[modelName].predict_proba(vectorizer.transform([commentText])) for modelName in models}
        for value in output.values():
            list.append(value[0][1])
        comment.obscene = list[0]
        comment.insult = list[1]
        comment.toxic = list[2]
        comment.severe_toxic = list[3]
        comment.identity_hate = list[4]
        comment.threat = list[5]
        comment.save()
        list.clear()

@api_view(['GET', 'POST'])
def profile(request):
    if request.method == 'GET':
        profiles = Profile.objects.all()
        serializer = profileSerializer(profiles, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = profileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
def profileData(request, pk):
    try:
        profile = Profile.objects.get(pk=pk)
    except profile.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = profileSerializer(profile)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = profileSerializer(profile, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
        # print(serializer)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def postData(request, pk):
    try:
        post = Post.objects.get(pk=pk)
    except post.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = postSerializer(post)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = postSerializer(post, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
            # classifyCommentsBy()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
def commentData(request, pk):
    try:
        comment = Comment.objects.get(pk=pk)
    except comment.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = commentSerializer(comment)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = commentSerializer(comment, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
