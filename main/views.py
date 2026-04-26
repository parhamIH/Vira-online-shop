from django.shortcuts import render , redirect
from shop.utils.cart_utils import get_cart_info
from django.contrib.auth.decorators import login_required
from shop.account.models import Notification 
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from shop.support.models import SupportTicket
from django.contrib.auth.models import User
from shop.products.models import  ProductPackage, Product 
from shop.cart.models import Cart, CartItem
from shop.categories.models import BaseCategorys, Category
from shop.home.models import  HomeSlider, FeaturedBrand, PromotionalBanner
from shop.public.models import Brand


def home(request):
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user, is_paid=False).first()
        cart_info = get_cart_info(cart) if cart else None
    else:
        cart = None  # مقداردهی cart برای کاربران ناشناس
        cart_info = None  # مدیریت حالت برای کاربران ناشناس

    # اگر cart وجود نداشت، cart_items را خالی قرار دهید
    cart_items = CartItem.objects.filter(cart=cart) if cart else []
    
    if cart_info is None:
        cart_info = {
            'cart_items': [],
            'cart_total': 0,
        }
    
    # دریافت دسته‌بندی‌های اصلی
    base_categories = BaseCategorys.objects.all()
    
    # دریافت اسلایدرهای فعال برای صفحه اصلی
    sliders = HomeSlider.objects.filter(active=True).order_by('order')
    
    # دریافت بنرهای تبلیغاتی فعال براساس موقعیت
    top_banners = PromotionalBanner.objects.filter(active=True, position='top').order_by('order')
    middle_banners = PromotionalBanner.objects.filter(active=True, position='middle').order_by('order')
    bottom_banners = PromotionalBanner.objects.filter(active=True, position='bottom').order_by('order')
    
    # دریافت برندهای ویژه فعال
    featured_brands = FeaturedBrand.objects.filter(active=True).select_related('brand').order_by('order')
    
    # دریافت محصولات پرفروش
    top_selling_products = ProductPackage.objects.filter(
        is_active_package=True
    ).select_related('product').order_by('-sold_count')[:10]  # نیاز به اضافه کردن فیلد sold_count به مدل ProductPackage
    
    # دریافت محصولات ویژه (محصولاتی که تخفیف دارند)
    special_products = ProductPackage.objects.filter(
        is_active_discount=True, 
        is_active_package=True
    ).select_related('product')[:10]  # محدود به 10 محصول
    
    # دریافت جدیدترین محصولات
    new_products = ProductPackage.objects.filter(
        is_active_package=True
    ).select_related('product').order_by('-created_date')[:10]  # محدود به 10 محصول
    
    search = request.GET.get("q")
    if search:
        return redirect(f"/products?q={search}")  # فرض بر این است که مسیر URL برای نتایج جستجو "/products" است
        
    context={
        "cart_items": [item for item in cart_info['cart_items']],  # اگر cart_items لیستی از CartItem باشد
        'cart_count': sum(item.count for item in cart_info['cart_items']),  # استفاده از ویژگی count از CartItem
        "cart_total": cart_info['cart_total'],  # استفاده از cart_total از تابع get_cart_info
        "base_categories": base_categories,  # دسته‌بندی‌های اصلی برای نمایش در صفحه اصلی
        "special_products": special_products,  # محصولات با تخفیف
        "new_products": new_products,  # جدیدترین محصولات
        "top_selling_products": top_selling_products,  # محصولات پرفروش
        "sliders": sliders,  # اسلایدرهای صفحه اصلی
        "top_banners": top_banners,  # بنرهای بالای صفحه
        "middle_banners": middle_banners,  # بنرهای وسط صفحه
        "bottom_banners": bottom_banners,  # بنرهای پایین صفحه
        "featured_brands": featured_brands,  # برندهای ویژه
    }
    
    return render (request,"../template/index.html",context) 
