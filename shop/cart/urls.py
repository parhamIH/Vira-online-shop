from django.urls import path
from .views import *


urlpatterns = [
    path("cart/", show_cart, name='cart'),
    path('delete-cart-item/', delete_CartItem, name='delete_cart_item'),
    path('update-cart-item/', update_CartItem),
    path('add-to-cart/', add_to_cart, name='add_to_cart'),  # اضافه کردن این مسیر
    path('get-cart-content/', get_cart_content, name='get_cart_content'),
    path('checkout/', checkout_view, name='checkout'),
    path('process-payment/', process_payment, name='process_payment'),
    path('bank-payment/', bank_payment_gateway, name='bank_payment_gateway'),
    path('verify-payment/', verify_payment, name='verify_payment'),
    path('order-invoice/<int:order_id>/', order_invoice, name='order_invoice'),
]
