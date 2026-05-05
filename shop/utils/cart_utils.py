from django.http import JsonResponse
from shop.cart.models import CartItem , Cart
from shop.products.models import ProductPackage
from django.db.models import Sum, F, FloatField, ExpressionWrapper

def get_cart_info(cart):
    valid_statuses = [
        'pending', 'confirmed', 'shipped', 'delivered', 'canceled',
        'لغو شده', 'تحویل داده شده', 'ارسال شده', 'تأیید شده', 'در حال انتظار'
    ]

    if not (cart and cart.status in valid_statuses):
        return {'cart_items': [], 'cart_total': 0}

    # گروه‌بندی و جمع‌بندی
    qs = (
        CartItem.objects
        .filter(cart=cart, package__isnull=False)
        .values('package_id')
        .annotate(
            total_count=Sum('count'),  # تعداد کل بر اساس پکیج
            unit_price=F('package__final_price'),  # قیمت واحد پکیج
            total_price=F('package__final_price') * Sum('count')  # قیمت کل پکیج
        )
    )

    # گرفتن جزئیات پکیج‌ها
    package_ids = [row['package_id'] for row in qs]
    packages = ProductPackage.objects.in_bulk(package_ids)

    cart_items = []
    cart_total = 0

    for row in qs:
        pid = row['package_id']
        package = packages.get(pid)
        if not package:
            continue

        total_price = row['total_price']
        cart_items.append({
            'package': package,
            'count': row['total_count'],
            'price': package.price,
            'total_price': total_price,
        })
        cart_total += total_price

    return {'cart_items': cart_items, 'cart_total': cart_total}

def get_cart_count(request):
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user, is_paid=False).first()
        cart_count = sum(item.count for item in CartItem.objects.filter(cart=cart)) if cart else 0
    else:
        cart_count = 0
    return JsonResponse({'cart_count': cart_count})

