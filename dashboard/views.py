import json
import joblib
import operator
import pandas as pd
import collections
import itertools
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse
from rest_framework import status
from .engine import SearchEngine
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import viewsets
from .models import *
from .serializers import *
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

def classify(id):
    if Comment.objects.filter(id=id).exists():
        model = Comment.objects.filter(id=id).first()
    else:
        model = Reply.objects.filter(id=id).first()
    list = []
    text = model.text
    models = {modelName: joblib.load('dashboard/models/' + modelName + '.pkl') for modelName in _MODEL_TYPE_NAMES}
    vectorizer = joblib.load('dashboard/models/' + 'vectorizer' + '.pkl')
    output = {modelName: models[modelName].predict_proba(vectorizer.transform([text])) for modelName in models}
    for value in output.values():
        list.append(value[0][1])
    model.obscene = list[0]
    model.insult = list[1]
    model.toxic = list[2]
    model.severe_toxic = list[3]
    model.identity_hate = list[4]
    model.threat = list[5]
    model.save()

def classifyComments(ts, post_id):
    comments = Comment.objects.filter(date_posted__gte=ts, post_id=post_id).exclude(date_posted__exact=ts)
    replies = Reply.objects.filter(date_posted__gte=ts, post_id=post_id).exclude(date_posted__exact=ts)
    for c in comments:
        classify(c.id)
    for r in replies:
        classify(r.id)
    return list(comments.values()) + list(replies.values())

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
        classifiedcomments = []
        allcomments = collections.defaultdict(list)
        for item in request.data:
            allcomments[item['post_id']].append(item)
        sortedcomments = list(allcomments.values())
        for comments in sortedcomments:
            comments.sort(key=operator.itemgetter('date_posted'))
            id = comments[0].get('post_id')
            post = Post.objects.filter(id=id).first()
            timestamp = post.ts
            for comment in comments:
                if Comment.objects.filter(id=comment.get('id')).exists():
                    serializer = commentSerializer(Comment.objects.get(id=comment.get('id')), data=comment, partial=True)
                else:
                    serializer = commentSerializer(data=comment)
                if serializer.is_valid():
                    serializer.save()
            classifiedcomments += classifyComments(timestamp, id)
        return Response(classifiedcomments, status=status.HTTP_200_OK)

