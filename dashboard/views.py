import json
import joblib
import operator
import pandas as pd
import collections
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse
from rest_framework import status
from .engine import SearchEngine
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import viewsets
from .models import Profile, Post, Comment, Reply
from .serializers import profileSerializer, postSerializer, commentSerializer, replySerializer
_MODEL_TYPE_NAMES = ['obscene', 'insult', 'toxic', 'severe_toxic', 'identity_hate', 'threat']
engine = SearchEngine()

def home(request):
    html = "<html><body>This is the site's homepage. </body></html>"
    return HttpResponse(html)

def getCommentsDf(fields = ['id', 'text', 'username', 'like_count', 'post_id']):
    comments = Comment.objects.all()
    serializer = commentSerializer(comments, many=True)
    df = pd.DataFrame(serializer.data, index=None)
    df['comment_id'] = [id for id in range(len(comments))]
    # data = [{}] * len(serializer.data)
    # print(len(serializer.data))
    # for idx, dataInstance in enumerate(serializer.data):
    #     print(dataInstance)
    return df

@api_view(['POST'])
def searchComment(request):
    global engine
    text = request.data['text']
    engine.target = 'text'
    engine.importDf(getCommentsDf(request.data['fields']))
    engine.buildIndex()
    return Response(engine.searchQuery(text, to_display=request.data['fields']))

def classifyCommentsBy(ts, post_id):
    comments = Comment.objects.filter(date_posted__gte=ts, post_id=post_id).exclude(date_posted__exact=ts)
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
    return comments

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
        classifiedComments = []
        comments = collections.defaultdict(list)
        for item in request.data:
            comments[item['post_id']].append(item)
        commentsSplitted = list(comments.values())
        for listOfComments in commentsSplitted:
            listOfComments.sort(key=operator.itemgetter('date_posted'))
            id = listOfComments[0].get('post_id')
            post = Post.objects.filter(id=id).first()
            timestamp = post.ts
            for item in listOfComments:
                if Comment.objects.filter(id=item.get('id')).exists():
                    serializer = commentSerializer(Comment.objects.get(id=item.get('id')), data=item, partial=True)
                else:
                    serializer = commentSerializer(data=item)
                if serializer.is_valid():
                    serializer.save()
            classifiedComments += classifyCommentsBy(timestamp, id).values()
        return Response(classifiedComments, status=status.HTTP_200_OK)

