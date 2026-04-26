from django.shortcuts import render, redirect , get_object_or_404
from django.http import JsonResponse, HttpResponseRedirect
from .models import Cart , Order , CartItem
from  utils.sms import send_sms
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from account.models import ClientAddress
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth.decorators import login_required
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
        # print("\n\n\n\n\ncart_info['cart_items'] in cart.views.showcart cart\n\n\n\n",cart_info['cart_items'])
        
        context = {
        'cart': cart,
        #_______________________________
        "cart_items": cart_info['cart_items'],  # اگر cart_items لیستی از CartItem باشد
        'cart_count': sum(item.count for item in cart_info['cart_items']),  # استفاده از ویژگی count از CartItem
        "cart_total": cart_info['cart_total'],  # استفاده از cart_total از تابع get_cart_info
        
        }
  # بررسی اینکه آیا سبد خرید خالی است یا خیر
        if not cart_info['cart_items']:
            return render(request, "template/cart-empty.html", context)

    else:
        return redirect("/template/login.html")
    

    return render(request, "template/cart.html", context)


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
        if hasattr(package, 'quantity') and count > package.quantity:
            return JsonResponse({
                'status': 'error',
                'message': f'موجودی محصول کافی نیست (حداکثر: {package.quantity})'
            }, status=400)
        
        # افزودن محصول به سبد خرید
        cart_item = CartItem.objects.create(cart=cart, package=package, count=count)
        
        # آماده‌سازی داده‌های پاسخ
        from utils import get_cart_info  # مسیر درست را وارد کنید
        cart_info = get_cart_info(cart)
        
        # تبدیل آبجکت‌های CartItem به دیکشنری ساده
        cart_items = []
        for item in cart_info['cart_items']:
            cart_items.append({
                'package_id': item.package.id,
                'product_id': item.package.product.id if hasattr(item.package, 'product') else None,
                'name': item.package.product.name if hasattr(item.package, 'product') else 'محصول',
                'count': item.count,
                'price': item.package.final_price,
                'original_price': item.package.price,
                'discount_price': item.package.discount_price if hasattr(item.package, 'discount_price') else None,
                'image': item.package.product.image.url if hasattr(item.package, 'product') and hasattr(item.package.product, 'image') else None,
                'is_active_discount': item.package.is_active_discount if hasattr(item.package, 'is_active_discount') else False
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
        
        # تبدیل آبجکت‌های CartItem به دیکشنری ساده
        cart_items = []
        for item in cart_info['cart_items']:
            cart_items.append({
                'package_id': item.package.id,
                'product_id': item.package.product.id if hasattr(item.package, 'product') else None,
                'name': item.package.product.name if hasattr(item.package, 'product') else 'محصول',
                'count': item.count,
                'price': item.package.final_price,
                'original_price': item.package.price,
                'discount_price': item.package.discount_price if hasattr(item.package, 'discount_price') else None,
                'image': item.package.product.image.url if hasattr(item.package, 'product') and hasattr(item.package.product, 'image') else None,
                'is_active_discount': item.package.is_active_discount if hasattr(item.package, 'is_active_discount') else False
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


def checkout_view(request):
    search = request.GET.get("q")
    if search:
        return redirect(f"/products?q={search}")
        
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user, is_paid=False).first()
        
        if not cart or not cart.cartitem_set.exists():
            messages.warning(request, "سبد خرید شما خالی است")
            return redirect('cart')
            
        # دریافت آدرس‌های کاربر
        addresses = ClientAddress.objects.filter(user=request.user)
        
        # محاسبه قیمت‌های ارسال
        shipping_costs = {
            'post': 50000,  # پست
            'tipax': 70000,  # تیپاکس
            'express': 80000,  # پیک موتوری
        }
        
        # تولید تاریخ‌های تحویل (6 روز آینده به صورت شمسی)
        delivery_dates = []
        try:
            import jdatetime
            today = jdatetime.datetime.now()
            for i in range(1, 7):
                future_date = today + jdatetime.timedelta(days=i)
                # تبدیل شماره روز هفته به نام روز
                day_names = ['دوشنبه', 'سه‌شنبه', 'چهارشنبه', 'پنج‌شنبه', 'جمعه', 'شنبه', 'یکشنبه']
                day_name = day_names[future_date.weekday()]
                
                # فرمت تاریخ به صورت "روز ماه"
                months_fa = ['فروردین', 'اردیبهشت', 'خرداد', 'تیر', 'مرداد', 'شهریور', 'مهر', 'آبان', 'آذر', 'دی', 'بهمن', 'اسفند']
                date_str = f"{future_date.day} {months_fa[future_date.month-1]}"
                
                # مقدار برای ارسال به سرور (تاریخ میلادی)
                gregorian_date = future_date.togregorian()
                date_value = gregorian_date.strftime('%Y-%m-%d')
                
                delivery_dates.append({
                    'day_name': day_name,
                    'date_str': date_str,
                    'value': date_value,
                    'jalali_date': f"{future_date.year}/{future_date.month}/{future_date.day}"
                })
        except ImportError:
            # اگر کتابخانه jdatetime نصب نبود، از تاریخ میلادی استفاده کن
            from datetime import datetime, timedelta
            today = datetime.now()
            for i in range(1, 7):
                future_date = today + timedelta(days=i)
                day_name = future_date.strftime("%A")
                date_str = future_date.strftime("%d %B")
                date_value = future_date.strftime('%Y-%m-%d')
                
                delivery_dates.append({
                    'day_name': day_name,
                    'date_str': date_str,
                    'value': date_value,
                    'jalali_date': date_str
                })
        
        # فعال‌سازی پرداخت در محل
        enable_cash_on_delivery = True  # می‌توانید بر اساس شرایط خاص تغییر دهید
        
        # لیست استان‌ها و شهرها (می‌توانید از مدل‌های مرتبط استفاده کنید)
        provinces = [
            {'id': 1, 'name': 'تهران'},
            {'id': 2, 'name': 'اصفهان'},
            {'id': 3, 'name': 'مازندران'},
            {'id': 4, 'name': 'گیلان'},
            {'id': 5, 'name': 'فارس'},
        ]
        
        cities = [
            {'id': 1, 'name': 'تهران', 'province_id': 1},
            {'id': 2, 'name': 'کرج', 'province_id': 1},
            {'id': 3, 'name': 'اصفهان', 'province_id': 2},
            {'id': 4, 'name': 'شیراز', 'province_id': 5},
        ]
        
        context = {
            'cart': cart,
            'addresses': addresses,
            'shipping_costs': shipping_costs,
            'delivery_dates': delivery_dates,
            'enable_cash_on_delivery': enable_cash_on_delivery,
            'provinces': provinces,
            'cities': cities,
        }
        return render(request, 'template/checkout.html', context)
    else:
        return redirect('login')


@login_required
def process_payment(request):
    """
    پردازش اطلاعات فرم پرداخت و ایجاد سفارش جدید
    """
    if request.method == 'POST':
        user = request.user
        cart = Cart.objects.filter(user=user, is_paid=False).first()
        
        # Log for debugging
        # print("Process Payment - POST request received")
        # print(f"Form data: {request.POST}")
        
        if not cart or not cart.cartitem_set.exists():
            messages.warning(request, "سبد خرید شما خالی است")
            return redirect('cart')
        
        # دریافت اطلاعات از فرم
        selected_address_id = request.POST.get('selected_address')
        shipping_method = request.POST.get('shipping_method', 'post')
        delivery_date = request.POST.get('delivery_date')
        payment_method = request.POST.get('payment_method', 'online')
        order_notes = request.POST.get('order_notes', '')
        
        # Log for debugging
        # print(f"Selected address ID: {selected_address_id}")
        # print(f"Shipping method: {shipping_method}")
        # print(f"Delivery date: {delivery_date}")
        # print(f"Payment method: {payment_method}")
        
        # تبدیل تاریخ میلادی به شمسی برای ذخیره
        jalali_delivery_date = None
        try:
            import jdatetime
            from datetime import datetime
            gregorian_date = datetime.strptime(delivery_date, '%Y-%m-%d').date()
            jdate = jdatetime.date.fromgregorian(date=gregorian_date)
            jalali_delivery_date = f"{jdate.year}/{jdate.month}/{jdate.day}"
        except (ImportError, ValueError) as e:
            print(f"Error converting date: {e}")
            jalali_delivery_date = delivery_date
        
        # اگر آدرس انتخاب نشده بود و کاربر آدرس جدید وارد کرده بود
        selected_address = None
        if not selected_address_id or not selected_address_id.strip():
            print("No address selected, creating new address")
            # ایجاد آدرس جدید
            try:
                new_address = ClientAddress(
                    user=user,
                    title_address=request.POST.get('title_address', ''),
                    province=request.POST.get('province', ''),
                    city=request.POST.get('city', ''),
                    full_address=request.POST.get('full_address', ''),
                    postcode=request.POST.get('postcode', '')
                )
                new_address.save()
                selected_address = new_address
                print(f"New address created with ID: {new_address.id}")
            except Exception as e:
                print(f"Error creating new address: {e}")
                import traceback
                traceback.print_exc()
                messages.error(request, "خطا در ثبت آدرس جدید")
                return redirect('checkout')
        else:
            try:
                selected_address = ClientAddress.objects.get(id=selected_address_id, user=user)
                print(f"Using existing address with ID: {selected_address.id}")
            except ClientAddress.DoesNotExist:
                print(f"Address with ID {selected_address_id} not found")
                messages.error(request, "آدرس انتخابی معتبر نیست")
                return redirect('checkout')
            except Exception as e:
                print(f"Error retrieving address: {e}")
                import traceback
                traceback.print_exc()
                messages.error(request, "خطا در دریافت آدرس")
                return redirect('checkout')
        
        if not selected_address:
            messages.error(request, "لطفاً یک آدرس انتخاب کنید یا آدرس جدید وارد نمایید")
            return redirect('checkout')
        
        # محاسبه هزینه ارسال
        shipping_costs = {
            'post': 50000,
            'tipax': 70000,
            'express': 80000,
        }
        shipping_cost = shipping_costs.get(shipping_method, shipping_costs['post'])
        
        # محاسبه قیمت نهایی سفارش
        total_price = cart.total_price() + shipping_cost
        # print(f"Total price: {total_price} (cart: {cart.total_price()} + shipping: {shipping_cost})")
        
        # ایجاد سفارش
        try:
            # بررسی اینکه آیا سفارشی قبلا با این سبد خرید ایجاد شده است
            existing_order = Order.objects.filter(cart=cart).first()
            if existing_order:
                # print(f"Found existing order for cart: {existing_order.id}")
                order = existing_order
                # بروزرسانی اطلاعات سفارش موجود
                order.address = selected_address
                order.shipping_method = shipping_method
                order.delivery_date = delivery_date
                order.jalali_delivery_date = jalali_delivery_date
                order.payment_method = payment_method
                order.shipping_cost = shipping_cost
                order.total_price = total_price
                order.notes = order_notes
                order.payment_status = 'در انتظار تایید'
                order.save()
                # print(f"Updated existing order with ID: {order.id}")
            else:
                # ایجاد سفارش جدید اگر قبلا وجود نداشت
                order = Order.objects.create(
                    user=user,
                    cart=cart,
                    address=selected_address,
                    shipping_method=shipping_method,
                    delivery_date=delivery_date,
                    jalali_delivery_date=jalali_delivery_date,
                    payment_method=payment_method,
                    shipping_cost=shipping_cost,
                    total_price=total_price,
                    notes=order_notes,
                    payment_status='در انتظار تایید'
                )
                # print(f"Order created successfully with ID: {order.id}")
            
            # اگر پرداخت آنلاین بود
            if payment_method == 'online':
                # print(f"Online payment - redirecting to payment gateway")
                # ذخیره شناسه سفارش در سشن برای استفاده بعد از پرداخت
                request.session['order_id'] = str(order.id)
                request.session.save()  # ذخیره صریح سشن
                # ارسال به درگاه پرداخت
                return redirect('bank_payment_gateway')
            else:
                # print(f"Cash on delivery payment")
                # پرداخت در محل
                order.status = "در حال انتظار"
                order.payment_status = 'در انتظار تایید'
                order.save()
                
                # علامت‌گذاری سبد خرید به عنوان پرداخت‌شده
                order.cart.is_paid = True
                order.cart.save()

                # کسر موجودی محصولات
                for item in cart.cartitem_set.all():
                    try:
                        package = item.package
                        if hasattr(package, 'quantity'): # Check if package has quantity field
                            package.quantity -= item.count
                            # Ensure quantity doesn't go below zero, though validation should prevent this
                            if package.quantity < 0:
                                package.quantity = 0
                            package.save()
                    except Exception as e:
                        # Log error if updating quantity fails for an item
                        print(f"Error updating quantity for package {package.id}: {e}")

                messages.success(request, "سفارش شما با موفقیت ثبت شد")
                # ارسال به صفحه فاکتور
                return redirect('order_invoice', order_id=order.id)
                
        except Exception as e:
            print(f"Error creating order: {e}")
            import traceback
            traceback.print_exc()
            messages.error(request, "خطا در ثبت سفارش")
            return redirect('checkout')
    else:
        # print("Non-POST request to process_payment view")
        pass # No action needed if not POST
    
    # اگر متد POST نبود یا مشکلی پیش آمد
    return redirect('checkout')

@login_required
def bank_payment_gateway(request):
    """
    این تابع کاربر را به درگاه بانک هدایت می‌کند
    """
    from django.conf import settings
    from .zarinpal import ZarinPal
    import traceback
    from django.http import HttpResponseRedirect
    
    # print("Bank Payment Gateway function called")
    
    order_id = request.session.get('order_id')
    # print(f"Order ID from session: {order_id}")
    
    if not order_id:
        # print("No order ID found in session")
        messages.error(request, "اطلاعات سفارش یافت نشد")
        return redirect('checkout')
    
    try:
        order = Order.objects.get(id=order_id, user=request.user)
        # print(f"Found order: {order.id}, total price: {order.total_price}")
    except Order.DoesNotExist:
        # print(f"Order with ID {order_id} not found for user {request.user.username}")
        messages.error(request, "سفارش مورد نظر یافت نشد")
        return redirect('checkout')
    except Exception as e:
        # print(f"Error retrieving order: {e}")
        traceback.print_exc()
        messages.error(request, "خطای سیستمی در بارگیری اطلاعات سفارش")
        return redirect('checkout')
    
    # اطلاعات مورد نیاز برای اتصال به درگاه پرداخت
    merchant_id = settings.ZARINPAL_SETTINGS.get('MERCHANT_ID')
    is_sandbox = settings.ZARINPAL_SETTINGS.get('SANDBOX', True)
    
    # print(f"ZarinPal settings - Merchant ID: {merchant_id}, Sandbox: {is_sandbox}")
    
    # بررسی اعتبار مرچنت آی دی
    if not merchant_id or merchant_id == 'XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX':
        # print("Invalid merchant ID")
        # برای تست در محیط توسعه، یک مرچنت آی دی پیش‌فرض برای محیط تست تنظیم می‌کنیم
        if is_sandbox:
            merchant_id = 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx'  # این یک مرچنت آی دی ساختگی برای تست است
            # print(f"Using dummy merchant ID for sandbox: {merchant_id}")
        else:
            messages.error(request, "خطا در تنظیمات درگاه پرداخت. لطفا با پشتیبانی تماس بگیرید.")
            return redirect('checkout')
    
    # تنظیم آدرس بازگشت
    callback_url = request.build_absolute_uri(reverse('verify_payment'))
    # print(f"Callback URL: {callback_url}")
    
    # ایجاد توضیحات
    order_number = getattr(order, 'order_number', order.id)
    description = f"پرداخت سفارش {order_number}"
    
    # راه اندازی زرین پال و درخواست پرداخت
    amount = int(order.total_price)  # مبلغ به تومان
    # print(f"Payment amount (Toman): {amount}")
    
    try:
        client = ZarinPal(merchant_id, callback_url, sandbox=is_sandbox)
        email = request.user.email if hasattr(request.user, 'email') and request.user.email else None
        result = client.payment_request(amount, description, email=email)
        
        # print(f"ZarinPal payment request result: {result}")
        
        if result.get('success', False):
            # ذخیره اطلاعات تراکنش در سشن
            request.session['zarinpal_authority'] = result['authority']
            request.session.save()  # ذخیره صریح سشن
            
            # انتقال مستقیم به درگاه زرین‌پال بدون رندر کردن قالب
            return HttpResponseRedirect(result['url'])
        else:
            # خطا در ایجاد درخواست پرداخت
            error_message = result.get('error', 'خطای نامشخص در اتصال به درگاه پرداخت')
            # print(f"Payment request failed: {error_message}")
            messages.error(request, error_message)
            return redirect('checkout')
    except Exception as e:
        # print(f"Exception in payment gateway: {e}")
        traceback.print_exc()
        
        # در صورت خطا در اتصال به درگاه، صفحه شبیه‌سازی تست نمایش دهیم
        if is_sandbox:
            context = {
                'order': order,
                'amount': amount,
                'merchant_id': merchant_id,
                'description': description,
                'callback_url': callback_url,
                'test_mode': True,
                'sandbox': is_sandbox,
                'error_message': str(e)
            }
            return render(request, 'direct_zarinpal.html', context)
        else:
            messages.error(request, f"خطای سیستمی: {str(e)}")
            return redirect('checkout')

@login_required
def verify_payment(request):
    """
    این تابع پس از بازگشت از درگاه پرداخت فراخوانی می‌شود
    """
    from django.conf import settings
    from .zarinpal import ZarinPal
    import traceback
    
    # print("Verify Payment function called")
    
    # دریافت پارامترهای برگشتی از درگاه پرداخت
    authority = request.GET.get('Authority')
    status = request.GET.get('Status')
    
    # print(f"Authority: {authority}, Status: {status}")
    
    # اگر پارامترهای برگشتی معتبر نباشند
    if not authority or not status:
        # print("Missing Authority or Status parameters")
        messages.error(request, "اطلاعات پرداخت معتبر نیست")
        return redirect('checkout')
    
    # اگر عملیات پرداخت لغو شده باشد
    if status != 'OK':
        # print("Payment was canceled or failed by user")
        messages.error(request, "عملیات پرداخت لغو شد")
        return redirect('checkout')
    
    # دریافت شناسه سفارش از سشن
    order_id = request.session.get('order_id')
    
    if not order_id:
        # print("No order_id found in session")
        messages.error(request, "اطلاعات سفارش یافت نشد")
        return redirect('checkout')
    
    try:
        order = Order.objects.get(id=order_id, user=request.user)
        # print(f"Found order with ID: {order.id}")
    except Order.DoesNotExist:
        # print(f"Order with ID {order_id} not found for user {request.user.username}")
        messages.error(request, "سفارش مورد نظر یافت نشد")
        return redirect('checkout')
    except Exception as e:
        # print(f"Error retrieving order: {e}")
        traceback.print_exc()
        messages.error(request, "خطای سیستمی در بازیابی اطلاعات سفارش")
        return redirect('checkout')
    
    # اطلاعات مورد نیاز برای تأیید پرداخت
    merchant_id = settings.ZARINPAL_SETTINGS.get('MERCHANT_ID')
    is_sandbox = settings.ZARINPAL_SETTINGS.get('SANDBOX', True)
    
    # print(f"ZarinPal settings - Merchant ID: {merchant_id}, Sandbox: {is_sandbox}")
    
    # آماده‌سازی آدرس بازگشت برای ارسال به ZarinPal
    callback_url = request.build_absolute_uri(reverse('verify_payment'))
    
    # استفاده از کلاس ZarinPal برای تأیید پرداخت
    try:
        client = ZarinPal(merchant_id, callback_url, sandbox=is_sandbox)
        result = client.payment_verification(authority, order.total_price)
        
        # print(f"Verification result: {result}")
        
        if result['success']:
            # پرداخت موفق - بروزرسانی سفارش و سبد خرید
            ref_id = result['ref_id']
            order.payment_reference_id = ref_id
            order.status = 'در حال انتظار'
            order.payment_status = 'پرداخت شده'
            order.save()
            
            # ارسال پیامک به کاربر پس از پرداخت موفق
            try:
                user_phone = request.user.profile.phone_number
                if user_phone:
                    message = f"سفارش شما با موفقیت ثبت و پرداخت شد. کد پیگیری: {ref_id}\nاز خرید شما متشکریم."
                    send_sms(user_phone, message)
            except Exception as e:
                # print(f"Error sending SMS to user: {e}")
                pass # No print for SMS sending

            # علامت‌گذاری سبد خرید به عنوان پرداخت‌شده
            order.cart.is_paid = True
            order.cart.save()

            # کسر موجودی محصولات
            cart = order.cart
            for item in cart.cartitem_set.all():
                try:
                    package = item.package
                    if hasattr(package, 'quantity'): # Check if package has quantity field
                        package.quantity -= item.count
                        # Ensure quantity doesn't go below zero
                        if package.quantity < 0:
                            package.quantity = 0 
                        package.save()
                except Exception as e:
                    # Log error if updating quantity fails for an item
                    # print(f"Error updating quantity for package {package.id} after online payment: {e}")
                    pass # No print for quantity update

            # پاک کردن شناسه سفارش از سشن
            if 'order_id' in request.session:
                del request.session['order_id']
            if 'zarinpal_authority' in request.session:
                del request.session['zarinpal_authority']
            
            # نمایش پیام موفقیت
            messages.success(request, f"پرداخت با موفقیت انجام شد. کد پیگیری: {ref_id}")
            
            # هدایت به صفحه فاکتور
            return redirect('order_invoice', order_id=order.id)
        else:
            # پرداخت ناموفق
            error_message = result.get('error', 'خطای نامشخص در تأیید پرداخت')
            status_code = result.get('status', -1)
            
            # print(f"Payment verification failed: {error_message} (code: {status_code})")
            
            # ثبت اطلاعات خطا در سفارش
            order.payment_status = 'ناموفق'
            order.payment_error = error_message
            order.save()
            
            # نمایش پیام خطا
            messages.error(request, f"تأیید پرداخت ناموفق بود: {error_message}")
            return redirect('checkout')
    
    except Exception as e:
        # print(f"Exception in payment verification: {e}")
        traceback.print_exc()
        messages.error(request, f"خطای سیستمی در تأیید پرداخت: {str(e)}")
        return redirect('checkout')

@login_required
def order_invoice(request, order_id):
    """
    نمایش فاکتور سفارش
    """
    try:
        order = Order.objects.get(id=order_id, user=request.user)
        cart = order.cart
        cart_items = cart.cartitem_set.all()
        
        # محاسبه مجموع قیمت‌ها و تخفیف‌ها
        total_price = sum(item.get_price() * item.count for item in cart_items)
        total_discount = sum((item.package.price - item.get_price()) * item.count for item in cart_items if item.package.price > item.get_price())
        
        
        # اطلاعات فروشگاه (می‌توانید از تنظیمات سایت دریافت کنید)
        store_info = {
            'name': 'فروشگاه آنلاین شاهان',
            'address': 'استان تهران، شهر تهران، خیابان ولیعصر، پلاک 123',
            'phone': '021-12345678',
            'postal_code': '1234567890',
            'economic_code': '123456789',
            'national_id': '10101010101',
        }
        
        # تبدیل تاریخ میلادی به شمسی
        try:
            import jdatetime
            from django.utils import timezone
            now = timezone.now()
            jnow = jdatetime.datetime.fromgregorian(datetime=now)
            date_str = f"{jnow.year}/{jnow.month}/{jnow.day}"
        except ImportError:
            from datetime import datetime
            date_str = datetime.now().strftime('%Y/%m/%d')
        
        context = {
            'order': order,
            'cart_items': cart_items,
            'total_price': total_price,
            'total_discount': total_discount,
            'final_price': total_price - total_discount + order.shipping_cost,
            'store_info': store_info,
            'date_str': date_str,
        }
        return render(request, 'template/factor.html', context)
    except Order.DoesNotExist:
        messages.error(request, "سفارش مورد نظر یافت نشد")
        return redirect('')
        