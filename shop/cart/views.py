from django.shortcuts import render, redirect 
from django.http import JsonResponse
from shop.cart.models import Cart, CartItem
from shop.products.models import  ProductPackage
from shop.utils.cart_utils import get_cart_count , get_cart_info 
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import json
import traceback

def show_cart(request):
        # مدیریت جستجو
    search = request.GET.get("q")
    if search:
        return redirect(f"/products?q={search}")

    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user, is_paid=False).first()
        
        # پردازش حذف آیتم
        if request.method == 'POST' and 'action' in request.POST and request.POST['action'] == 'delete_item':
            package_id = request.POST.get('package_id')
            if package_id:
                try:
                    cart_items = CartItem.objects.filter(cart=cart, package_id=package_id)
                    if cart_items.exists():
                        cart_items.delete()
                        # بارگذاری مجدد صفحه پس از حذف
                        return redirect('show_cart')
                except Exception as e:
                    print(f"Error deleting cart item: {e}")
        
        # استفاده از تابع get_cart_info برای دریافت اطلاعات سبد خرید
        cart_info = get_cart_info(cart)
        
        context = {
        'cart': cart,
        #_______________________________
        "cart_items": cart_info['cart_items'],  # اگر cart_items لیستی از CartItem باشد
        'cart_count': sum(item["count"] for item in cart_info['cart_items']),  # استفاده از ویژگی count از CartItem
        "cart_total": cart_info['cart_total'],  # استفاده از cart_total از تابع get_cart_info
        
        }
  # بررسی اینکه آیا سبد خرید خالی است یا خیر
        if not cart_info['cart_items']:
            return render(request, "frontend/template/cart-empty.html", context)

    else:
        return redirect("frontend//template/login.html")
    

    return render(request, "frontend/template/cart.html", context)


@require_POST
def delete_CartItem(request):
    if request.method == 'POST' and request.user.is_authenticated:
        # پذیرش هر دو فرمت JSON و form-data
        if request.content_type and 'application/json' in request.content_type:
            try:
                data = json.loads(request.body)
                package_id = data.get('package_id')
            except:
                package_id = None
        else:
            package_id = request.POST.get('package_id')
        
        if not package_id or not str(package_id).isdigit():
            return JsonResponse({'status': 'error', 'message': 'شناسه پکیج نامعتبر است'}, status=400)

        try:
            # یافتن سبد خرید فعال کاربر
            cart = Cart.objects.filter(user=request.user, is_paid=False).first()
            if not cart:
                return JsonResponse({'status': 'error', 'message': 'سبد خرید پیدا نشد'}, status=404)

            # حذف آیتم از سبد خرید
            cart_items = CartItem.objects.filter(package_id=package_id, cart=cart)
            deleted_count, _ = cart_items.delete()
            
            if deleted_count == 0:
                return JsonResponse({'status': 'error', 'message': 'هیچ آیتمی حذف نشد'}, status=404)

            # محاسبه تعداد باقی‌مانده آیتم‌ها و قیمت‌ها
            remaining_count = CartItem.objects.filter(cart=cart).count()
            
            # محاسبه قیمت‌ها - استفاده از متدهای موجود در مدل Cart
            total_goods_price = cart.total_goods_price() if hasattr(cart, 'total_goods_price') else 0
            total_discount = cart.total_discount() if hasattr(cart, 'total_discount') else 0
            total_price = cart.total_price() if hasattr(cart, 'total_price') else 0
            
            # اگر متدهای مذکور وجود ندارند، محاسبه دستی انجام شود
            if not hasattr(cart, 'total_price'):
                total_price = sum(item.package.final_price * item.count for item in CartItem.objects.filter(cart=cart))
                cart.save()
            
            return JsonResponse({
                'status': 'success', 
                'message': 'محصول با موفقیت از سبد خرید حذف شد',
                'cart_items_count': remaining_count,  # تعداد آیتم‌های سبد خرید
                'total_goods_price': total_goods_price,
                'total_discount': total_discount,
                'total_price': total_price
            })
        
        except Exception as e:
            print(f"Error in delete_CartItem: {str(e)}")  # لاگ خطا برای دیباگ
            traceback.print_exc()  # نمایش جزئیات خطا در لاگ
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
    else:
        return JsonResponse({'status': 'error', 'message': 'لطفا وارد شوید'}, status=401)


@require_POST
def update_CartItem(request):
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': 'لطفا وارد شوید'}, status=401)
        
    
    try:
        # دریافت داده‌های درخواست
        data = json.loads(request.body)
        package_id = data.get('package_id')
        count = int(data.get('count', 1))
        
        # بررسی داده‌ها
        if not package_id:
            return JsonResponse({'status': 'error', 'message': 'شناسه پکیج الزامی است'}, status=400)
        if count < 1:
            return JsonResponse({'status': 'error', 'message': 'تعداد باید حداقل 1 باشد'}, status=400)
        
        # دریافت سبد خرید
        cart, created = Cart.objects.get_or_create(user=request.user, is_paid=False)
        
        # دریافت پکیج
        try:
            package = ProductPackage.objects.get(id=package_id)
        except ProductPackage.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'پکیج مورد نظر یافت نشد'}, status=404)
        
        # بررسی موجودی
        if count > package.quantity:
            return JsonResponse({
                'status': 'error', 
                'message': f'موجودی محصول کافی نیست (حداکثر: {package.quantity})'
            }, status=400)
        
        # به‌روزرسانی یا ایجاد آیتم سبد خرید
        cart_item, item_created = CartItem.objects.get_or_create(
            cart=cart,
            package=package,
            defaults={'count': count}
        )
        
        if not item_created:
            cart_item.count = count
            cart_item.save()
        
        # محاسبه قیمت‌ها (فراخوانی متدها با پرانتز)
        item_total_price = cart_item.package.final_price * cart_item.count
        total_goods_price = cart.total_goods_price()
        total_discount = cart.total_discount()
        total_price = cart.total_price()
        cart_items_count = cart.cartitem_set.count()
        
        # برگرداندن پاسخ
        return JsonResponse({
            'status': 'success',
            'message': 'سبد خرید به‌روزرسانی شد',
            'package_id': package_id,
            'count': count,
            'item_total_price': item_total_price,
            'total_goods_price': total_goods_price,
            'total_discount': total_discount,
            'total_price': total_price,
            'cart_items_count': cart_items_count
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'داده‌های نامعتبر'}, status=400)
    except Exception as e:
        print(f"Error in update_CartItem: {str(e)}")
        traceback.print_exc()
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@csrf_exempt
@require_POST
def add_to_cart(request):
    """
    ویو افزودن محصول به سبد خرید
    """
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': 'لطفا وارد شوید'}, status=401)
    
    try:
        # دریافت داده‌های درخواست
        package_id = request.POST.get('package-id')
        count = int(request.POST.get('count', 1))
        
        # اعتبارسنجی داده‌های ورودی
        if not package_id:
            return JsonResponse({'status': 'error', 'message': 'شناسه پکیج الزامی است'}, status=400)
        
        if count < 1:
            count = 1
        
        # دریافت سبد خرید فعلی کاربر یا ایجاد یک سبد جدید
        cart, created = Cart.objects.get_or_create(user=request.user, is_paid=False)
        
        # بررسی اینکه آیا محصول قبلاً در سبد خرید است
        existing_item = CartItem.objects.filter(cart=cart, package_id=package_id).first()
        if existing_item:
            return JsonResponse({
                'status': 'warning',
                'message': 'این محصول قبلاً در سبد خرید شما موجود است',
                'cart_items_count': cart.cartitem_set.count(),
            }, status=200)
        
        # دریافت پکیج محصول
        try:
            package = ProductPackage.objects.get(id=package_id)
        except ProductPackage.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'پکیج مورد نظر یافت نشد'}, status=404)
        
        # بررسی موجودی محصول
        # if hasattr(package, 'quantity') and count > package.quantity:

        if getattr(package, 'quantity', None) is not None and count > package.quantity:
            return JsonResponse({
                'status': 'error',
                'message': f'موجودی محصول کافی نیست (حداکثر: {package.quantity})'
            }, status=400)
        
        # افزودن محصول به سبد خرید
        cart_item = CartItem.objects.create(cart=cart, package=package, count=count)
        
        # آماده‌سازی داده‌های پاسخ
        from shop.utils.cart_utils import get_cart_info  # مسیر درست را وارد کنید
        cart_info = get_cart_info(cart)
        print("package_id:", package_id)
        print("count:", request.POST.get('countt'))

        cart_items = []
        for item in cart_info['cart_items']:
            package = item['package']
            cart_items.append({
                'package_id': package.id,
                'product_id': package.product.id if hasattr(package, 'product') else None,
                'name': package.product.name if hasattr(package, 'product') else 'محصول',
                'count': item['count'],
                'price': package.final_price,   # یا item['price']
                'original_price': package.price,
                'discount_price': package.discount_price if hasattr(package, 'discount_price') else None,
                'image': package.product.image.url if hasattr(package, 'product') and hasattr(package.product, 'image') else None,
                'is_active_discount': package.is_active_discount if hasattr(package, 'is_active_discount') else False
            })

        return JsonResponse({
            'status': 'success',
            'message': 'محصول با موفقیت به سبد خرید اضافه شد',
            'cart_items_count': len(cart_items),
            'cart_items': cart_items,
            'cart_total': cart_info['cart_total']
        })
        
    except ValueError as e:
        # خطای تبدیل نوع داده (مثلاً تبدیل رشته به عدد)
        return JsonResponse({'status': 'error', 'message': 'مقدار نامعتبر: ' + str(e)}, status=400)
    
    except Exception as e:
        # ثبت خطا برای بررسی بیشتر
        print(f"Error in add_to_cart: {str(e)}")
        traceback.print_exc()
        return JsonResponse({'status': 'error', 'message': 'خطای سرور: ' + str(e)}, status=500)


def get_cart_content(request):
    """دریافت محتوای سبد خرید برای به‌روزرسانی in offcanvas"""
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': 'لطفا وارد شوید'}, status=401)
    
    try:
        # دریافت سبد خرید فعال کاربر
        cart = Cart.objects.filter(user=request.user, is_paid=False).first()
        
        if not cart:
            return JsonResponse({
                'status': 'success',
                'cart_items_count': 0,
                'cart_items': []
            })
        
        # استفاده از تابع get_cart_info برای دریافت اطلاعات سبد خرید
        cart_info = get_cart_info(cart)
        
        cart_items = []
        for item in cart_info['cart_items']:
            package = item['package']
            cart_items.append({
                'package_id': package.id,
                'product_id': package.product.id if hasattr(package, 'product') else None,
                'name': package.product.name if hasattr(package, 'product') else 'محصول',
                'count': item['count'],
                'price': package.final_price,   # یا item['price']
                'original_price': package.price,
                'discount_price': package.discount_price if hasattr(package, 'discount_price') else None,
                'image': package.product.image.url if hasattr(package, 'product') and hasattr(package.product, 'image') else None,
                'is_active_discount': package.is_active_discount if hasattr(package, 'is_active_discount') else False
            })

        return JsonResponse({
            'status': 'success',
            'cart_items_count': len(cart_items),
            'cart_items': cart_items,
            'cart_total': cart_info['cart_total']
        })
        
    except Exception as e:
        print(f"Error in get_cart_content: {str(e)}")
        traceback.print_exc()
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

