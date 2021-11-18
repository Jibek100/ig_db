from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='dashboard-home'),
    path('classifycomments/<int:pk>', views.classifyComment, name="dashboard-classify-comment"),
    path('classifycomments/', views.classifyComments, name="dashboard-classify-comments"),
    path('profiles/', views.profile, name="dashboard-profiles"),
    path('profiles/<int:pk>', views.profileData, name="dashboard-profileData"),
    path('posts/', views.post, name="dashboard-posts"),
    path('posts/<int:pk>', views.postData, name="dashboard-postData"),
    path('comments/', views.comment, name="dashboard-comments"),
    path('comments/<int:pk>', views.commentData, name="dashboard-commentData"),
    path('replies/', views.reply, name="dashboard-replies"),
    path('replies/<int:pk>', views.replyData, name="dashboard-replyData")
]
