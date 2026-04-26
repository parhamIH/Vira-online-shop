from django.urls import path
from . import views

urlpatterns = [
    path('', views.articles, name='articles'),
    path('<str:slug>/', views.article_detail, name='article_detail'),
]
