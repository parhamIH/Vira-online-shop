from django.urls import path
from shop.providers.views import *
from django.shortcuts import get_object_or_404, redirect
from django.utils.text import slugify


urlpatterns = [
    path("register", register_provider ),

]
    