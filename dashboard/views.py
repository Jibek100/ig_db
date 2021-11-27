import pandas as pd
import joblib
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse
from rest_framework import status
from .engine import SearchEngine
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import viewsets
from emoji import UNICODE_EMOJI
from instagram_scraper.constants import *
from .models import Profile, Post, Comment, Reply
from .serializers import profileSerializer, postSerializer, commentSerializer, replySerializer
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

def classifyCommentsBy(ts):
    comments = Comment.objects.filter(date_posted__gte=ts)
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
        if Profile.objects.filter(id=request.data.get('id')).exists():
            serializer = profileSerializer(Profile.objects.get(id=request.data.get('id')), data=request.data, partial=True)
        else:
            serializer = profileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET', 'POST'])
def post(request):
    if request.method == 'GET':
        posts = Post.objects.all()
        serializer = postSerializer(posts, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        for item in request.data:
            if Post.objects.filter(id=item.get('id')).exists():
                serializer = postSerializer(Post.objects.get(id=item.get('id')), data=item, partial=True)
            else:
                serializer = postSerializer(data=item)
            if serializer.is_valid():
                serializer.save()
        return Response(status=status.HTTP_200_OK)

@api_view(['GET', 'POST'])
def comment(request):
    if request.method == 'GET':
        comments = Comment.objects.all()
        serializer = commentSerializer(comments, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        post = Post.objects.get(id=request.data[0].get('post_id'))
        timestamp = post.ts
        for item in request.data:
            serializer = commentSerializer(data=item)
            if serializer.is_valid():
                serializer.save()
        classifyCommentsBy(timestamp)
        return Response(status=status.HTTP_200_OK)

@api_view(['GET'])
def emoji_list():
    comments = Comment.objects.all()
    for comment in comments:
        data = regex.findall(r'\X', comment.text)
        for word in data:
            if any(char in emoji.UNICODE_EMOJI for char in word):
                emoji_list.append(word)
        data = []
    return Response(emoji_list)

def getProfile(username):
    argv = 'instagram scraper ' + username
    return execute_from_command_line(argv)
