from django.urls import path
from shop.products.views import *
from django.shortcuts import get_object_or_404, redirect
from django.utils.text import slugify


urlpatterns = [
    path("products", products_list),
    path('product/<pk>/<name>', product_detail, name='product_detail'),
    path ("categories/<en_name>", category_products),    
    path("get-package-info/<int:package_id>/", get_package_info, name='get_package_info'),
    path("page/<slug:slug>/", static_page, name='static_page'),
    path('get-sizes/', get_sizes_for_color, name='get_sizes_for_color'),
]
    