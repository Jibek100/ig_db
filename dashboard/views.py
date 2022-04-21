import os
import glob
import shutil
import json
import joblib
import operator
import pandas as pd
import collections
import instaloader
import itertools
import emoji
import re
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse
from rest_framework import status
from .engine import SearchEngine
from .model import DistilBertForSequenceClassification
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import viewsets
from django.db.models import Count
from sklearn.manifold import TSNE
from .models import *
from .serializers import *
from .test import *

_MODEL_TYPE_NAMES = ['obscene', 'insult', 'toxic', 'severe_toxic', 'identity_hate', 'threat']
engine = SearchEngine()
igloader = instaloader.Instaloader()
config = DistilBertConfig(
    vocab_size=32000, hidden_dim=768,
    dropout=0.1, num_labels=6,
    n_layers=12, n_heads=12,
    intermediate_size=3072)
state_dict = torch.load('dashboard/models/distilbert_model_weights.pth', map_location=DEVICE)
model = DistilBertForSequenceClassification(config)
model.load_state_dict(state_dict=state_dict)
model.to(DEVICE)


def home(request):
    html = "<html><body>This is the site's homepage. </body></html>"
    return HttpResponse(html)


def getCommentsDf(fields=['id', 'text', 'username', 'like_count', 'post_id']):
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


def classifyComments(ts, post_id):
    comments = Comment.objects.filter(date_posted__gte=ts, post_id=post_id).exclude(date_posted__exact=ts)
    replies = Reply.objects.filter(date_posted__gte=ts, post_id=post_id).exclude(date_posted__exact=ts)
    dataset = list(comments.values_list('text', flat=True)) + list(replies.values_list('text', flat=True))
    test_dataset = text_dataset(dataset)
    prediction_dataloader = torch.utils.data.DataLoader(test_dataset, batch_size=1, shuffle=False)
    predictions = preds(model=model, test_loader=prediction_dataloader)
    predictions = np.array(predictions)[:, 0]
    for i in range(len(comments)):
        comments[i].toxic = predictions[i, 0]
        comments[i].severe_toxic = predictions[i, 1]
        comments[i].obscene = predictions[i, 2]
        comments[i].threat = predictions[i, 3]
        comments[i].insult = predictions[i, 4]
        comments[i].identity_hate = predictions[i, 5]
        comments[i].save()
    for i in range(len(replies)):
        replies[i].toxic = predictions[i+len(comments), 0]
        replies[i].severe_toxic = predictions[i+len(comments), 1]
        replies[i].obscene = predictions[i+len(comments), 2]
        replies[i].threat = predictions[i+len(comments), 3]
        replies[i].insult = predictions[i+len(comments), 4]
        replies[i].identity_hate = predictions[i+len(comments), 5]
        replies[i].save()

    return list(comments.values()) + list(replies.values())


@api_view(['POST'])
def searchUsername(request):
    comments = list(Comment.objects.filter(username=request.data['username']).values()) + list(Reply.objects.filter(username=request.data['username']).values())
    return Response(comments, status=status.HTTP_200_OK)


def getProfilePics():
    global igloader
    users = Username.objects.all()
    for user in users:
        name = user.username
        profile = igloader.check_profile_id(name.lower())
        igloader.download_profilepic(profile)
        for jpgfile in glob.iglob(os.path.join(name, "*.jpg")):
            shutil.move(jpgfile, "photos/" + name + ".jpg")
        shutil.rmtree(name)
        user.photo = "photos/" + name + ".jpg"
        user.bio = remove_emoji(profile.biography)
        user.site = profile.external_url
        if checkBio(user.site):
            user.contains_link = True
        user.save()


@api_view(['GET'])
def commentsToPlane(request):
    comments = Comment.objects.all()
    replies = Reply.objects.all()
    dataset = list(comments.values_list('text', flat=True)) + list(replies.values_list('text', flat=True))
    test_dataset = text_dataset(dataset)
    prediction_dataloader = torch.utils.data.DataLoader(test_dataset, batch_size=1, shuffle=False)
    planes = text_to_2d_plane(model=model, test_loader=prediction_dataloader)
    for i in range(len(comments)):
        comments[i].x = planes[i][0]
        comments[i].y = planes[i][1]
        comments[i].save()
    for i in range(len(replies)):
        replies[i].x = planes[i+len(comments)][0]
        replies[i].y = planes[i+len(comments)][1]
        replies[i].save()
    return Response(list(comments.values('id', 'text', 'x', 'y', 'username'))+list(replies.values('id', 'text', 'x', 'y', 'username')), status=status.HTTP_200_OK)


def remove_emoji(string):
    return emoji.get_emoji_regexp().sub(u'', string)


def checkBio(string):
    return re.search(".ly|.bio", string)


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
            ts = post.ts
            for comment in comments:
                if Comment.objects.filter(id=comment.get('id')).exists():
                    serializer = commentSerializer(Comment.objects.get(id=comment.get('id')), data=comment, partial=True)
                else:
                    serializer = commentSerializer(data=comment)
                if serializer.is_valid():
                    serializer.save()
            classifiedcomments += classifyComments(ts, id)
            getProfilePics()
        return Response(classifiedcomments, status=status.HTTP_200_OK)


@api_view(['GET'])
def username(request):
    if request.method == 'GET':
        users = Username.objects.all()
        serializer = usernameSerializer(users, many=True)
        return Response(serializer.data)


