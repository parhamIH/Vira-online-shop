from django.http import JsonResponse
from shop.cart.models import CartItem , Cart
from shop.products.models import ProductPackage
from django.db.models import Sum, F, BigIntegerField, ExpressionWrapper

def get_cart_info(cart):
    if not cart:
        return {'cart_items': [], 'cart_total': 0}

    qs = (
        CartItem.objects
        .filter(cart=cart, package__isnull=False)
        .values('package_id')
        .annotate(total_count=Sum('count'))
    )

    package_ids = [row['package_id'] for row in qs]
    packages = ProductPackage.objects.select_related('product').in_bulk(package_ids)

    cart_items = []
    cart_total = 0

    for row in qs:
        package = packages.get(row['package_id'])
        if not package:
            continue

        total_price = package.final_price * row['total_count']

        cart_items.append({
            'package':package,
            'package_id': package.id,
            'name': package.product.name,
            'image': package.product.image.url if package.product.image else '',
            'count': row['total_count'],
            'price': package.final_price,  # ✅ قیمت نهایی
            'original_price': package.price,  # ✅ قیمت قبل تخفیف
            'is_active_discount': package.is_active_discount,
            'total_price': total_price,
        })

        cart_total += total_price

    return {
        'cart_items': cart_items,
        'cart_total': cart_total,
    }

def get_cart_count(request):
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user, is_paid=False).first()
        cart_count = sum(item.count for item in CartItem.objects.filter(cart=cart)) if cart else 0
    else:
        cart_count = 0
    return JsonResponse({'cart_count': cart_count})

