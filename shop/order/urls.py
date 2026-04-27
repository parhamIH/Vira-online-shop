from django.urls import path
from shop.order.views import *


urlpatterns = [
    path('checkout/', checkout_view, name='checkout'),
    path('process-payment/', process_payment, name='process_payment'),
    path('bank-payment/', bank_payment_gateway, name='bank_payment_gateway'),
    path('verify-payment/', verify_payment, name='verify_payment'),
    path('order-invoice/<int:order_id>/', order_invoice, name='order_invoice'),
]
