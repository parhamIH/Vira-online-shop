from django.http import JsonResponse
from shop.cart.models import CartItem , Cart

def get_cart_info(cart):
    valid_statuses = ['pending', 'confirmed', 'shipped', 'delivered', 'canceled' ,
                       'لغو شده','تحویل داده شده','ارسال شده','تأیید شده','در حال انتظار']
    if cart and cart.status in valid_statuses:
        cart_items = CartItem.objects.filter(cart=cart)
        cart_items_new = []
        
        # ایجاد دیکشنری برای نگهداری تعداد آیتم‌ها بر اساس پکیج
        package_counts = {}

        # شمارش تعداد آیتم‌ها بر اساس پکیج
        for item in cart_items:
            if item.package:
                package_id = item.package.id  # شناسه پکیج
                if package_id in package_counts:
                    package_counts[package_id] += item.count  # افزایش تعداد
                else:
                    package_counts[package_id] = item.count  # شروع شمارش

        # ایجاد لیست جدید با آیتم‌ها و تعداد آن‌ها
        for package_id, count in package_counts.items():
            new_item = CartItem(package_id=package_id, count=count)
            cart_items_new.append(new_item)

        return {
            'cart_items': cart_items_new,
            "cart_total": cart.total_price(),
        }
    else:
        return {
            'cart_items': [],
            "cart_total": 0,
        }

def get_cart_count(request):
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user, is_paid=False).first()
        cart_count = sum(item.count for item in CartItem.objects.filter(cart=cart)) if cart else 0
    else:
        cart_count = 0
    return JsonResponse({'cart_count': cart_count})

