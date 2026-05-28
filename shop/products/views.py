from django.shortcuts import render , redirect ,get_object_or_404
from django.core.paginator import Paginator
from shop.categories.models import BaseCategories, Category
from shop.cart.models import  CartItem ,Cart
from shop.products.models import Product, ProductPackage, Gallery
from shop.public.models import Size, Brand, BaseColor
from shop.reviews.models import Comment
from shop.sitesettings.models import StaticPage

from shop.utils.cart_utils import get_cart_info
from django.http import JsonResponse 
import json 
from django.db.models import Count, Q
from django.views.decorators.csrf import csrf_exempt  # اگر با CSRF مشکل دارید
from django.contrib.auth.decorators import login_required
from shop.account.models import FavouriteProducts 
from django.template.loader import render_to_string
from django.utils.text import slugify


#products
def products_list(request):

    # ORM
    base_categories = BaseCategories.objects.all()
    categories = Category.objects.all()
    all_sizes = Size.objects.all()
    base_colors = BaseColor.objects.all()
    brands = Brand.objects.all()

    # بررسی کنید که آیا کاربر احراز هویت شده است
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user, is_paid=False).first()
        cart_info = get_cart_info(cart) if cart else None
    else:
        cart_info = None  # مدیریت حالت برای کاربران ناشناس



    # فیلترها
    package = ProductPackage.objects.select_related("product").all()

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
    if selected_categories:
        package = package.filter(product__categories__en_name__in=selected_categories)

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
    # print(f"\n\n\n\n shopapp produnct list function  ---- base_categories:{base_categories.values()}\n\n categories:{categories.values()}")
    
    context = {
        "base_categories": base_categories,
        "categories": categories,
        "current_page": current_page,
        "sizes": all_sizes,
        "brands": brands,
        "base_colors": base_colors,
        "cart_items": cart_info['cart_items'] if cart_info else [],
        'cart_count': sum(item['count'] for item in cart_info['cart_items']) if cart_info else 0,
        "cart_total": cart_info['cart_total'] if cart_info else 0,
        # اضافه کردن لیست مقادیر فیلتر شده به context
        "selected_categories": selected_categories,
        "selected_colors": selected_colors,
        "selected_sizes": selected_sizes,
        "selected_brands": selected_brands,
    }
    
 
    return render(request, "frontend/template/products.html", context)


#products
def product_detail(request, *args, **kwargs):

    # دریافت محصول با استفاده از pk
    product = get_object_or_404(Product, id=kwargs['pk'])
    categories = product.categories.all()
    gallery = Gallery.objects.filter(product=product)
    comments = Comment.objects.filter(product=product)
    packages = ProductPackage.objects.filter(product=product)

    # حذف بسته‌هایی که نامعتبرند
    packages = packages.exclude(quantity__lte=0, is_active_package=False)

    # دریافت مشخصات محصول


    more_products = ProductPackage.objects.filter(
        product__categories__in=categories
    ).exclude(
        product__id=product.id
    ).select_related('product').distinct()[:10]  # محدود به 10 محصول برای بهبود کارایی
    # اطلاعات سبد خرید
    cart = None
    cart_items = []
    cart_package_ids = []
    cart_items_json = []

    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user, is_paid=False).first()
        if cart:
            cart_items = CartItem.objects.filter(cart=cart)
            cart_package_ids = [item.package.id for item in cart_items]
            # print(f"\n\n\n\ncart_package_ids:{cart_package_ids}\ncart_items:{cart_items}\n\n\n\n\n\n\n\n")
            cart_items_json = [
                {
                    'package': {'id': item.package.id, 'quantity': item.package.quantity},
                    'count': item.count
                } for item in cart_items
            ]

    # ایجاد دیکشنری رنگ‌های یکتا
    unique_colors = {}
    for package in packages:
        if package.color.id not in unique_colors:
            unique_colors[package.color.id] = package.color

    product_needs_color_or_size = packages.exists()

    # مدیریت جستجو
    search = request.GET.get("q")
    if search:
        return redirect(f"/products?q={search}")

    user_favorites = []
    if request.user.is_authenticated:
        fav_obj = FavouriteProducts.objects.filter(user=request.user).first()
        if fav_obj:
            user_favorites = fav_obj.products.all()

    # بررسی اینکه آیا محصول در لیست علاقه‌مندی‌های کاربر است یا خیر
    is_favorite = False
    if request.user.is_authenticated:
        fav_obj = FavouriteProducts.objects.filter(user=request.user).first()
        if fav_obj and product in fav_obj.products.all():
            is_favorite = True

    selected_color_id = request.GET.get("color-options")
    if selected_color_id and selected_color_id.isdigit():
        selected_color_id = int(selected_color_id)
        packages = packages.filter(color__id=selected_color_id)
    else:
        selected_color_id = None  # به وضوح مقداردهی کن
    # print("\n\n\n\n\n dashchagh",product_specifications,"\n\n\n\n\n")
    # مقداردهی اولیه `context`
    context = {
        "categories": categories,
        "product": product,
        "gallery": gallery,
        "comments": comments,
        "more_products": more_products,
        "packages": packages,
        "unique_colors": unique_colors.values(),
        "cart_items": cart_items,
        "cart_count": sum(item.count for item in cart_items) if cart_items else 0,
        "cart_total": sum(item.package.price * item.count for item in cart_items) if cart_items else 0,
        "product_needs_color_or_size": product_needs_color_or_size,
        "cart_package_ids": cart_package_ids,
        "cart_items_json": json.dumps(cart_items_json),  # تبدیل به JSON برای جاوااسکریپت
        'user_favorites': user_favorites,
        'is_favorite': is_favorite,
        "selected_color_id": selected_color_id,  # ✅ اضافه شد

    }

    # بررسی درخواست‌های POST
    if request.method == "POST":
        if not request.user.is_authenticated:
            return redirect("/login")

        package_to_cart = request.POST.get("package-id")  # مقدار id بسته انتخاب‌شده
        if package_to_cart:
            # print(f"\n\n\n\n\n\n POST req -> PD: {request.POST} \n\n\n\n\n ")
            try:
                package_id = int(package_to_cart)  # تبدیل مقدار به عدد
            except ValueError:
                return redirect(request.path)  # مقدار نامعتبر، ری‌دایرکت شود

            package = ProductPackage.objects.filter(id=package_id, product=product).first()
            if package:
                if not cart:
                    cart = Cart.objects.create(user=request.user)

                # بررسی وجود بسته در سبد خرید و افزودن یا به‌روزرسانی
                cart_item, created = CartItem.objects.get_or_create(
                    cart=cart,
                    package=package,
                    defaults={'count': int(request.POST.get('count', 1))}  # مقدار پیش‌فرض 1
                )
                if not created:
                    cart_item.count += int(request.POST.get('count', 1))
                    cart_item.save()

                # print(f"\n\n\n post package pd \n\n\n\n\n\ncart: {cart}")
        return redirect(request.path)  # پس از افزودن به سبد خرید، صفحه رفرش شود

    return render(request, "frontend/template/product.html", context)

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


#products
def get_package_info(request, package_id):
    try:
        package = ProductPackage.objects.get(id=package_id)
        return JsonResponse({
            'status': 'success',
            'package': {
                'price': package.price,
                'discount_price': package.final_price if package.is_active_discount else None,
                'original_price': package.price,
                'quantity': package.quantity
            }
        })
    except ProductPackage.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'پکیج یافت نشد'
        }, status=404)


#cart
# برای کاربران مهمان
@csrf_exempt
def add_to_cart(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            product_id = data.get('product_id')
            
            # اگر کاربر وارد شده است
            if request.user.is_authenticated:
                # افزودن به سبد خرید کاربر
                cart, created = Cart.objects.get_or_create(user=request.user)
                product_package = ProductPackage.objects.get(id=product_id)
                cart_item, created = CartItem.objects.get_or_create(cart=cart, product_package=product_package)
                
                if not created:
                    cart_item.quantity += 1
                    cart_item.save()
                
                # محاسبه تعداد کل آیتم‌های سبد خرید
                cart_count = sum(item.quantity for item in CartItem.objects.filter(cart=cart))
            else:
                # افزودن به سبد خرید session-based برای کاربران مهمان
                cart = request.session.get('cart', {})
                cart[product_id] = cart.get(product_id, 0) + 1
                request.session['cart'] = cart
                
                # محاسبه تعداد کل آیتم‌های سبد خرید
                cart_count = sum(cart.values())
            
            return JsonResponse({
                'success': True, 
                'message': 'محصول به سبد خرید اضافه شد',
                'cart_count': cart_count
            })
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'خطا: {str(e)}'})
    
    return JsonResponse({'success': False, 'message': 'درخواست نامعتبر'})

#product
# برای افزودن به علاقه‌مندی‌ها
@csrf_exempt
def add_to_wishlist(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            product_id = data.get('product_id')
            
            # بررسی ورود کاربر
            if request.user.is_authenticated:
                product = Product.objects.get(id=product_id)
                wishlist, created = Wishlist.objects.get_or_create(user=request.user)
                
                # بررسی وجود محصول در علاقه‌مندی‌ها
                if product in wishlist.products.all():
                    # اگر محصول قبلاً در لیست باشد، حذف می‌شود
                    wishlist.products.remove(product)
                    return JsonResponse({'success': True, 'message': 'محصول از علاقه‌مندی‌ها حذف شد', 'action': 'removed'})
                else:
                    # افزودن محصول به لیست علاقه‌مندی‌ها
                    wishlist.products.add(product)
                    return JsonResponse({'success': True, 'message': 'محصول به علاقه‌مندی‌ها اضافه شد', 'action': 'added'})
            else:
                return JsonResponse({'success': False, 'message': 'برای افزودن به علاقه‌مندی‌ها باید وارد شوید'})
                
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'خطا: {str(e)}'})
    
    return JsonResponse({'success': False, 'message': 'درخواست نامعتبر'})


def static_page(request, slug):
    """
    نمایش صفحات استاتیک مانند درباره ما، قوانین و مقررات و...
    """
    # دریافت صفحه بر اساس slug
    page = get_object_or_404(StaticPage, slug=slug, active=True)
    
    # بررسی و مدیریت جستجو
    search = request.GET.get("q")
    if search:
        return redirect(f"/products?q={search}")
    
    # اطلاعات سبد خرید
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user, is_paid=False).first()
        cart_info = get_cart_info(cart) if cart else None
    else:
        cart_info = None
    
    if cart_info is None:
        cart_info = {
            'cart_items': [],
            'cart_total': 0,
        }
        
    context = {
        "page": page,
        "cart_items": [item for item in cart_info['cart_items']],
        'cart_count': sum(item.count for item in cart_info['cart_items']),
        "cart_total": cart_info['cart_total'],
        
        "meta_title": page.seo_title or page.title,
        "meta_description": page.seo_description or "",
        "meta_keywords": page.seo_keywords or "",
    }
    
    return render(request, "frontend/template/static_page.html", context)

#product
def get_sizes_for_color(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        color_id = request.GET.get('color_id')
        product_id = request.GET.get('product_id')
        
        if color_id and product_id:
            packages = ProductPackage.objects.filter(
                product_id=product_id,
                color_id=color_id,
                is_active_package=True
            ).select_related('size')
            
            html = render_to_string('partials/_size_options.html', {
                'packages': packages
            })
            
            return JsonResponse({'html': html})
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

