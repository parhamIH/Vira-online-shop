from cart.models import CartItem , Cart
from shopApp.models import * 
from django.http import JsonResponse



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

def validate_iranian_national_id(national_id):
    """
    اعتبارسنجی کد ملی ایرانی
    
    شرایط کد ملی معتبر:
    1. دقیقاً 10 رقم باشد
    2. همه کاراکترها عدد باشند
    3. الگوریتم اعتبارسنجی کد ملی را پاس کند
    
    ساختار کد ملی:
    - 9 رقم اول: شماره اصلی
    - رقم دهم: رقم کنترلی
    """
    # بررسی طول کد ملی
    if not national_id or len(national_id) != 10:
        return False
    
    # بررسی عددی بودن تمام کاراکترها
    if not national_id.isdigit():
        return False
    
    # بررسی الگوی کدهای ملی غیرمعتبر مانند 0000000000 و 1111111111
    if national_id in ['0000000000', '1111111111', '2222222222', '3333333333', 
                      '4444444444', '5555555555', '6666666666', '7777777777', 
                      '8888888888', '9999999999']:
        return False
    
    # محاسبه رقم کنترلی
    check = int(national_id[9])
    sum_digits = 0
    
    for i in range(9):
        sum_digits += int(national_id[i]) * (10 - i)
    
    remainder = sum_digits % 11
    
    if remainder < 2:
        return check == remainder
    else:
        return check == 11 - remainder
