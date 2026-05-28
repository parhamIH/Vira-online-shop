from django.shortcuts import render , get_object_or_404
from django.core.paginator import Paginator
from .models import BaseCategories , Category
from shop.utils.cart_utils import get_cart_info
from shop.public.models import Brand , BaseColor
from shop.products.models import Size , ProductPackage
from shop.cart.models import Cart

# Create your views here.

#category
def category_products(request, en_name):
    # دریافت دسته‌بندی اصلی
    base_category = get_object_or_404(BaseCategories, en_name=en_name)
    
    # ORM - دریافت اطلاعات مورد نیاز
    base_categories = BaseCategories.objects.all()
    categories = Category.objects.filter(base_catgory=base_category)
    all_sizes = Size.objects.all()
    base_colors = BaseColor.objects.all()
    brands = Brand.objects.all()
    
    # بررسی کنید که آیا کاربر احراز هویت شده است
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user, is_paid=False).first()
        cart_info = get_cart_info(cart) if cart else None
    else:
        cart_info = None  # مدیریت حالت برای کاربران ناشناس
    
    # فیلترها - فقط محصولات مربوط به دسته‌بندی انتخاب شده
    package = ProductPackage.objects.select_related("product").filter(
        product__categories__in=categories,
        product__is_active=True
    )
    
    # مرتب‌سازی
    orderby = request.GET.get("orderby")
    if orderby == "date":
        package = package.order_by("created_date")
    elif orderby == "higher-price":
        package = package.order_by("-final_price")
    elif orderby == "is_active_discount":
        package = package.filter(is_active_discount=True)
    elif orderby == "is_active":
        package = package.filter(is_active_package=True)
    elif orderby == "lower-price":
        package = package.order_by("final_price")
    
    # فیلتر دسته‌بندی
    selected_categories = request.GET.getlist('category')
    
    # فیلتر سایز
    selected_sizes = request.GET.getlist('size')
    if selected_sizes:
        # تبدیل selected_sizes به لیست اندیس‌های شروع از 1
        size_indices = [int(size_index) for size_index in selected_sizes if size_index.isdigit()]
        if size_indices:
            # دریافت سایزهای انتخاب شده بر اساس اندیس
            size_objects = Size.objects.all()
            selected_size_ids = []
            for i, size_obj in enumerate(size_objects, 1):
                if i in size_indices:
                    selected_size_ids.append(size_obj.id)
            if selected_size_ids:
                package = package.filter(size__id__in=selected_size_ids)
    
    # فیلتر رنگ
    selected_colors = request.GET.getlist('color')
    if selected_colors:
        package = package.filter(color__name__in=selected_colors)
    
    # فیلتر برند
    selected_brands = request.GET.getlist('brand')
    if selected_brands:
        package = package.filter(brand__en_name__in=selected_brands)
    
    # فیلتر قیمت
    price_min = request.GET.get("price_min", "0").strip()
    price_max = request.GET.get("price_max", "9000000000009").strip()
    
    if price_min.isdigit() and price_max.isdigit():
        price_min = int(price_min)
        price_max = int(price_max)
        package = package.filter(final_price__range=(price_min, price_max))
    
    # جستجو
    search = request.GET.get("q")
    if search:
        package = package.filter(product__name__icontains=search)
    
    # جلوگیری از تکرار محصولات بر اساس id
    unique_package_ids = set()
    unique_packages = []
    
    for pkg in package:
        if pkg.product.id not in unique_package_ids:
            unique_packages.append(pkg)
            unique_package_ids.add(pkg.product.id)
    
    # Paginator
    page = request.GET.get("page")
    products_paginator = Paginator(unique_packages, 15)  # 15 محصول در هر صفحه
    current_page = products_paginator.get_page(page)
    
    context = {
        "base_categories": base_categories,
        "categories": categories,
        "base_category": base_category,  # اضافه کردن دسته‌بندی انتخاب شده
        "current_page": current_page,
        "sizes": all_sizes,
        "brands": brands,
        "base_colors": base_colors,
        "cart_items": cart_info['cart_items'] if cart_info else [],
        'cart_count': sum(item.count for item in cart_info['cart_items']) if cart_info else 0,
        "cart_total": cart_info['cart_total'] if cart_info else 0,
        # اضافه کردن لیست مقادیر فیلتر شده به context
        "selected_categories": selected_categories,
        "selected_colors": selected_colors,
        "selected_sizes": selected_sizes,
        "selected_brands": selected_brands,
    }
    
    # print(f"Total category products: {len(unique_packages)}")
    
    return render(request, "frontend/template/category.html", context)

