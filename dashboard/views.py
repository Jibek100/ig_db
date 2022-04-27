import os
import glob
import shutil
import json
import joblib
import operator
import numpy as np
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
from .test2 import *
from .utils import *

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
    dataset = list(comments.values_list('text', flat=True))
    test_dataset = text_dataset(dataset)
    prediction_dataloader = torch.utils.data.DataLoader(test_dataset, batch_size=10, shuffle=False)
    predictions = preds(model=model, test_loader=prediction_dataloader)
    for i in range(len(comments)):
        comments[i].toxic = predictions[i][0]
        comments[i].severe_toxic = predictions[i][1]
        comments[i].obscene = predictions[i][2]
        comments[i].threat = predictions[i][3]
        comments[i].insult = predictions[i][4]
        comments[i].identity_hate = predictions[i][5]
        comments[i].save()

    dataset_replies = list(replies.values_list('text', flat=True))
    test_dataset_replies = text_dataset(dataset_replies)
    prediction_dataloader_replies = torch.utils.data.DataLoader(test_dataset_replies, batch_size=10, shuffle=False)
    predictions_replies = preds(model=model, test_loader=prediction_dataloader_replies)
    for i in range(len(replies)):
        replies[i].toxic = predictions_replies[i][0]
        replies[i].severe_toxic = predictions_replies[i][1]
        replies[i].obscene = predictions_replies[i][2]
        replies[i].threat = predictions_replies[i][3]
        replies[i].insult = predictions_replies[i][4]
        replies[i].identity_hate = predictions_replies[i][5]
        replies[i].save()

    return list(comments.values()) + list(replies.values())

def getProfilePics():
    global igloader
    users = Username.objects.all()
    for user in users:
        name = user.username
        profile = igloader.check_profile_id(name.lower())
        igloader.download_profilepic(profile)
        for jpgfile in glob.iglob(os.path.join(name, "*.jpg")):
            shutil.move(jpgfile, "dashboard/folder/folder/" + name + ".jpg")
        shutil.rmtree(name)
        user.photo = "dashboard/folder/folder/" + name + ".jpg"
        user.bio = remove_emoji(profile.biography)
        user.site = profile.external_url
        # if checkBio(user.site):
        #     user.contains_link = True
        user.save()

@api_view(['GET'])
def getPhishingIndexes(request):
    set_seed(42)
    phishingmodel = MobileNetClf()
    device = torch.device('cpu')
    phishingmodel.load_state_dict(torch.load('dashboard/models/best_model_resnet18.pt', map_location=device))

    img_size = 320
    pretrained_means = [0.485, 0.456, 0.406]
    pretrained_stds = [0.229, 0.224, 0.225]

    test_transforms = transforms.Compose([
        transforms.Resize(img_size),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=pretrained_means,
            std=pretrained_stds)
    ])

    test_data = ImageFolderWithPaths(
        root='dashboard/folder',
        transform=test_transforms)

    test_iterator = data.DataLoader(
        test_data,
        batch_size=64)

    phishingmodel.to(device)
    phishingmodel.eval()
    preds, paths = [], []
    with torch.no_grad():
        for x, y, path in tqdm(test_iterator, desc='Eval'):
            x = x.to(device)
            y = y.to(device)

            preds += phishingmodel(x).tolist()
            paths += path
    for i in range(len(preds)):
        name = getName(paths[i])
        user = Username.objects.filter(username=name).first()
        user.nudity_indicator = 1-preds[i]
        user.save()
    return Response(list(Username.objects.all().values('username', 'site','nudity_indicator')), status=status.HTTP_200_OK)

def getName(string):
    return string.split("folder\\folder\\")[1].split(".jpg")[0]

def commentsToPlane():
    comments = Comment.objects.all()
    replies = Reply.objects.all()
    dataset = list(comments.values_list('text', flat=True))
    test_dataset = text_dataset(dataset)
    prediction_dataloader = torch.utils.data.DataLoader(test_dataset, batch_size=10, shuffle=False)
    planes = text_to_2d_plane(model=model, test_loader=prediction_dataloader)
    for i in range(len(comments)):
        comments[i].x = planes[i][0]
        comments[i].y = planes[i][1]
        comments[i].save()
    dataset_replies = list(replies.values_list('text', flat=True))
    test_dataset_replies = text_dataset(dataset_replies)
    prediction_dataloader_replies = torch.utils.data.DataLoader(test_dataset_replies, batch_size=10, shuffle=False)
    planes_replies = text_to_2d_plane(model=model, test_loader=prediction_dataloader_replies)
    for i in range(len(replies)):
        replies[i].x = planes_replies[i][0]
        replies[i].y = planes_replies[i][1]
        replies[i].save()


def remove_emoji(string):
    return emoji.get_emoji_regexp().sub(u'', string)


def checkBio(string):
    return re.search(".ly", string)


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
            # commentsToPlane()
        return Response(classifiedcomments, status=status.HTTP_200_OK)


@api_view(['GET'])
def username(request):
    if request.method == 'GET':
        users = Username.objects.all()
        serializer = usernameSerializer(users, many=True)
        return Response(serializer.data)


