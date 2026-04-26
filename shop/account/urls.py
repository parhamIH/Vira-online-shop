from django.urls import path
from shop.account.views import *

urlpatterns = [
    path('register/', register_user, name='register'),
    path('verify-registration/', verify_registration, name='verify_registration'),
    path('resend-registration-code/', resend_registration_code, name='resend_registration_code'),
    path('login/', login_user, name='login'),
    path('phone-login/', phone_login, name='phone_login'),
    path('verify-code/', verify_code, name='verify_code'),
    path("profile/",panel, name='panel'),
    path("profile/notification",user_notifications, name='user_notifications'),
    path("profile/informations",edit_user_informations, name='edit_profile'),
    path("profile/address",edit_client_address),
    path('profile/list/',liked_list),
    path('profile/orders',user_orders),
    path('logout/', user_logout, name='logout'),
    path("cart/items/<int:cart_id>/", get_cart_items, name="cart-items"),
    path('profile/favorites/add/', add_to_favorites, name='add_to_favorites'),
    path('profile/favorites/remove/', remove_from_favorites, name='remove_from_favorites'),
    path('profile/comments/', user_comments, name='user_comments'),
    
    # Password reset URLs
    path('reset-password-request/', reset_password_request, name='reset_password_request'),
    path('verify-reset-code/', verify_reset_code, name='verify_reset_code'),
    path('set-new-password/', set_new_password, name='set_new_password'),
    path('profile/offers', user_offers, name='user_offers'),
]
