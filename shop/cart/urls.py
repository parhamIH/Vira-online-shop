from django.urls import path
from shop.cart.views import *


urlpatterns = [
    path("cart/", show_cart, name='cart'),
    path('cart/delete-cart-item/', delete_CartItem, name='delete_cart_item'),
    path('update-cart-item/', update_CartItem),
    path('add-to-cart/', add_to_cart, name='add_to_cart'),  # اضافه کردن این مسیر
    path('get-cart-content/', get_cart_content, name='get_cart_content'),

]
