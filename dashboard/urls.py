from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='dashboard-home'),
    path('searchcomment/', views.searchComment, name="dashboard-search-comment"),
    path('profiles/', views.profile, name="dashboard-profiles"),
    path('posts/', views.post, name="dashboard-posts"),
    path('comments/', views.comment, name="dashboard-comments"),
]
