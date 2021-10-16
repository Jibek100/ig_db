from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='dashboard-home'),
    path('profiles/', views.profile, name="dashboard-profiles"),
    path('profiles/<int:pk>', views.profileData, name="dashboard-profileData"),
    path('posts/', views.post, name="dashboard-posts"),
    path('posts/<int:pk>', views.postData, name="dashboard-postData"),
    # path('comments/', views.comment, name="dashboard-comments"),
    # path('replies/', views.reply, name="dashboard-replies")
]
