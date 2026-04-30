from django.http import JsonResponse
from shop.cart.models import CartItem , Cart
from shop.products.models import ProductPackage

def get_cart_info(cart):
    valid_statuses = [
        'pending', 'confirmed', 'shipped', 'delivered', 'canceled',
        'لغو شده', 'تحویل داده شده', 'ارسال شده', 'تأیید شده', 'در حال انتظار'
    ]
    
    if cart and cart.status in valid_statuses:
        cart_items = CartItem.objects.filter(cart=cart)
        package_counts = {}

        # شمارش بر اساس package_id
        for item in cart_items:
            if item.package:
                pid = item.package.id
                package_counts[pid] = package_counts.get(pid, 0) + item.count

        cart_items_new = []
        total_price = 0

        # ساخت ساختار تمیز برای پاسخ
        for pid, count in package_counts.items():
            package = ProductPackage.objects.get(id=pid)
            total = package.final_price * count  
            cart_items_new.append({
                'package': package,
                'count': count,
                'price': package.price,
                'total_price': total,
            })
            total_price += total

        return {'cart_items': cart_items_new, 'cart_total': total_price}

    return {'cart_items': [], 'cart_total': 0}


def get_cart_count(request):
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user, is_paid=False).first()
        cart_count = sum(item.count for item in CartItem.objects.filter(cart=cart)) if cart else 0
    else:
        cart_count = 0
    return JsonResponse({'cart_count': cart_count})

