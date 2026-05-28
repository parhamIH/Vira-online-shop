from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth import authenticate, login , logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from shop.account.models import FavouriteProducts, ClientAddress, Notification, Profile, UserCoupon
from shop.cart.models import Cart, CartItem
from shop.order.models import Order
from shop.reviews.models import Comment
from django.db.models import Min, F
from django.views.decorators.http import require_POST
from datetime import datetime
from django.utils import timezone
from shop.utils.sms import generate_verification_code, send_verification_sms, is_verification_code_expired
from shop.account.models import validate_iranian_national_id
from shop.products.models import Product , ProductPackage
from shop.utils.cart_utils import get_cart_info

@login_required(login_url='/login/')
def user_logout(request):
    logout(request)
    return redirect("/")

def login_user(request):
    if request.user.is_authenticated:
        return redirect("/profile")
    
    # در صفحه لاگین، پیام‌های فلش مربوط به پروفایل را پاک کن
    # لیست پیام‌هایی که باید حفظ شوند
    keep_messages = []
    # کلمات کلیدی برای تشخیص پیام‌های مربوط به لاگین و ثبت‌نام
    login_keywords = ['ورود', 'ثبت نام', 'نام کاربری', 'رمز عبور', 'ایمیل', 'شماره تلفن', 'قوانین', 'کد تأیید']
    
    if hasattr(request, '_messages'):
        messages_to_keep = []
        for message in messages.get_messages(request):
            # اگر پیام مربوط به لاگین یا ثبت‌نام است، آن را نگه دار
            should_keep = False
            for keyword in login_keywords:
                if keyword in str(message):
                    should_keep = True
                    break
            
            if should_keep:
                messages_to_keep.append(message)
        
        # پاک کردن همه پیام‌ها
        storage = messages.get_messages(request)
        for _ in storage:
            pass  # پاک کردن همه پیام‌ها با گذر از آن‌ها
        
        # اضافه کردن دوباره پیام‌های مرتبط با لاگین
        for message in messages_to_keep:
            messages.add_message(request, message.level, message.message)
    
    context = {}
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Check if username and password are provided
        if not username or not password:
            context = {
                'login_invalid': "لطفا نام کاربری و رمز عبور را وارد کنید"
            }
            return render(request, 'frontend/template/login.html', context)
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)        
            return redirect("/products")
        else:
            context = {
                'login_invalid': "نام کاربری یا رمز عبور شما اشتباه است"
            }
            return render(request, 'frontend/template/login.html', context)
        
    return render(request, 'frontend/template/login.html', context)

def register_user(request):
    if request.method == 'POST':
        phone_number = request.POST.get('phone_number')
        if not phone_number or len(phone_number) != 11 or not phone_number.startswith('09'):
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'error', 'message': 'شماره موبایل معتبر نیست'})
            messages.error(request, 'شماره موبایل معتبر نیست')
            return render(request, 'frontend/template/login.html')
        if Profile.objects.filter(phone_number=phone_number).exists() or User.objects.filter(username=phone_number).exists():
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'error', 'message': 'این شماره قبلاً ثبت شده است'})
            messages.error(request, 'این شماره قبلاً ثبت شده است')
            return render(request, 'frontend/template/login.html')
        code = generate_verification_code()
        request.session['registration_phone'] = phone_number
        request.session['registration_code'] = code
        request.session['registration_code_created_at'] = datetime.now().timestamp()
        success, response = send_verification_sms(phone_number, code)
        if success:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'success', 'message': 'کد تأیید ارسال شد'})
            return render(request, 'frontend/template/verify_registration.html', {'phone_number': phone_number})
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'error', 'message': f'خطا در ارسال پیامک: {response}'})
            messages.error(request, f'خطا در ارسال پیامک: {response}')
            return render(request, 'frontend/template/login.html')
    return render(request, 'frontend/template/login.html')

def verify_registration(request):
    if request.method == 'POST':
        phone_number = request.POST.get('phone_number')
        code = request.POST.get('code')
        session_phone = request.session.get('registration_phone')
        session_code = request.session.get('registration_code')
        code_created_at = request.session.get('registration_code_created_at')
        # اعتبارسنجی کد و شماره
        if (phone_number != session_phone or code != session_code):
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'error', 'message': 'کد تأیید اشتباه است'})
            messages.error(request, 'کد تأیید اشتباه است')
            return render(request, 'frontend/template/verify_registration.html', {'phone_number': phone_number})
        # بررسی انقضای کد
        from datetime import datetime
        from utils.sms import is_verification_code_expired
        if code_created_at:
            code_created_at_dt = datetime.fromtimestamp(code_created_at)
            if is_verification_code_expired(code_created_at_dt):
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'status': 'error', 'message': 'کد تأیید منقضی شده است'})
                messages.error(request, 'کد تأیید منقضی شده است')
                return render(request, 'frontend/template/verify_registration.html', {'phone_number': phone_number})
        # ساخت کاربر جدید
        try:
            user = User.objects.create_user(username=phone_number, password=User.objects.make_random_password())
            profile = Profile.objects.get(user=user)
            profile.phone_number = phone_number
            profile.is_phone_verified = True
            profile.save()
            login(request, user)
            # پاکسازی session
            for key in ['registration_phone', 'registration_code', 'registration_code_created_at']:
                if key in request.session: del request.session[key]
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'success', 'message': 'ثبت‌نام با موفقیت انجام شد'})
            return redirect('/profile')
        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'error', 'message': f'خطا در ثبت‌نام: {str(e)}'})
            messages.error(request, f'خطا در ثبت‌نام: {str(e)}')
            return render(request, 'frontend/template/verify_registration.html', {'phone_number': phone_number})
    return redirect('/login/')

def resend_registration_code(request):
    """ارسال مجدد کد تأیید برای ثبت نام"""
    if request.method == 'POST':
        # بررسی وجود اطلاعات ثبت نام در سشن
        if 'registration_info' not in request.session:
            messages.error(request, 'اطلاعات ثبت نام نامعتبر است. لطفا دوباره تلاش کنید')
            return redirect('/login/')
        
        phone_number = request.session['registration_info']['phone_number']
        
        # تولید کد جدید
        code = generate_verification_code()
        request.session['registration_code'] = code
        request.session['registration_code_created_at'] = datetime.now().timestamp()
        
        # ارسال پیامک
        success, response = send_verification_sms(phone_number, code)
        
        context = {
            'phone_number': phone_number,
            'registration_mode': True
        }
        
        if success:
            context['success'] = 'کد تأیید جدید به شماره تلفن شما ارسال شد'
        else:
            context['error'] = f'خطا در ارسال پیامک: {response}'
        
        return render(request, 'frontend/template/verify_registration.html', context)
    
    return redirect('/login/')

def phone_login(request):
    """ارسال کد تأیید به شماره تلفن کاربر"""
    if request.user.is_authenticated:
        return redirect("/profile")
    
    context = {}
    
    if request.method == 'POST':
        phone_number = request.POST.get('phone_number')
        
        if not phone_number:
            context['error'] = "لطفا شماره تلفن خود را وارد کنید"
            return render(request, 'frontend/template/phone_login.html', context)
        
        try:
            profile = Profile.objects.get(phone_number=phone_number)
            
            # تولید کد تأیید و ذخیره آن
            code = generate_verification_code()
            profile.verification_code = code
            profile.verification_code_created_at = timezone.now()
            profile.save()
            
            # ارسال پیامک
            success, response = send_verification_sms(phone_number, code)
            
            # بررسی ارسال مجدد کد با استفاده از ریفرر
            referer = request.META.get('HTTP_REFERER', '')
            is_resend = 'verify-code' in referer
            
            if success:
                if is_resend:
                    context['success'] = "کد تأیید جدید به شماره تلفن شما ارسال شد"
                else:
                    context['success'] = "کد تأیید به شماره تلفن شما ارسال شد"
                
                context['phone_number'] = phone_number
                return render(request, 'frontend/template/verify_code.html', context)
            else:
                context['error'] = f"خطا در ارسال پیامک: {response}"
                if is_resend:
                    context['phone_number'] = phone_number
                    return render(request, 'frontend/template/verify_code.html', context)
                else:
                    return render(request, 'frontend/template/phone_login.html', context)
                
        except Profile.DoesNotExist:
            context['error'] = "این شماره تلفن در سیستم ثبت نشده است"
            return render(request, 'frontend/template/phone_login.html', context)
    
    return render(request, 'frontend/template/phone_login.html', context)

def verify_code(request):
    """تأیید کد ارسال شده به شماره تلفن کاربر"""
    if request.user.is_authenticated:
        return redirect("/profile")
    
    context = {}
    
    if request.method == 'POST':
        phone_number = request.POST.get('phone_number')
        code = request.POST.get('code')
        
        if not phone_number or not code:
            context['error'] = "لطفا شماره تلفن و کد تأیید را وارد کنید"
            return render(request, 'frontend/template/verify_code.html', context)
        
        try:
            profile = Profile.objects.get(phone_number=phone_number, verification_code=code)
            
            # بررسی انقضای کد تأیید
            if is_verification_code_expired(profile.verification_code_created_at):
                context['error'] = "کد تأیید منقضی شده است. لطفا مجددا تلاش کنید"
                context['phone_number'] = phone_number
                return render(request, 'frontend/template/verify_code.html', context)
            
            # ورود کاربر
            profile.is_phone_verified = True
            profile.save()
            login(request, profile.user)
            
            # پاک کردن کد تأیید پس از ورود موفق
            profile.verification_code = None
            profile.save()
            
            return redirect('/profile')
            
        except Profile.DoesNotExist:
            context['error'] = "کد تأیید نامعتبر است"
            context['phone_number'] = phone_number
            return render(request, 'frontend/template/verify_code.html', context)
    
    return render(request, 'frontend/template/verify_code.html', context)

@login_required(login_url='/login/')
def panel(request):
    context = get_common_context(request)
    search = request.GET.get("q")
    if search:
        return redirect(f"/products?q={search}")
    
    # Get last 10 orders for the user
    orders = Order.objects.filter(user=request.user).order_by('-order_date')[:10]
    context['orders'] = orders
    
    return render(request, 'frontend/template/panel.html', context)



@login_required(login_url='/login/')
def user_orders(request):
    '''
    order-item.html --> for show on modal BS
    '''
    search = request.GET.get("q")
    if search:
        return redirect(f"/products?q={search}")
        
    # Get orders instead of carts
    orders = Order.objects.filter(user=request.user).order_by('-order_date')
    context = get_common_context(request)
    context['orders'] = orders
    
    return render(request, "frontend/template/order.html", context)



@login_required(login_url='/login/')
def get_cart_items(request, cart_id):
    try:
        cart = Cart.objects.get(id=cart_id, user=request.user)
        items = cart.cartitem_set.all()

        # سعی در یافتن سفارش مرتبط با این سبد خرید
        try:
            order = Order.objects.get(cart=cart)
            order_data = {
                "order_number": order.order_number,
                "order_date": order.order_date.strftime("%Y/%m/%d %H:%M:%S") if order.order_date else None,
                "status": order.status,
                "payment_status": order.payment_status,
                "payment_method": order.get_payment_method_display() if hasattr(order, 'get_payment_method_display') else order.payment_method,
                "payment_reference_id": order.payment_reference_id,
                "shipping_method": order.get_shipping_method_display() if hasattr(order, 'get_shipping_method_display') else order.shipping_method,
                "shipping_cost": order.shipping_cost,
                "shipping_date": order.shipping_date.strftime("%Y/%m/%d") if order.shipping_date else None,
                "delivery_date": order.jalali_delivery_date or (order.delivery_date.strftime("%Y/%m/%d") if order.delivery_date else None),
                "total_price": order.total_price,
                "discount_amount": order.discount_amount,
                "final_price": order.calculate_total() if hasattr(order, 'calculate_total') else order.total_price
            }
        except Order.DoesNotExist:
            order_data = {}

        if not items:
            return JsonResponse({"error": "هیچ آیتمی در سبد خرید نیست", **order_data}, status=400)

        items_data = []
        for item in items:
            # محاسبه قیمت کل برای هر آیتم
            total_price = item.get_price() * item.count
            
            item_data = {
                "name": item.package.product.name,
                "count": item.count,
                "price": item.get_price(),
                "total_price": total_price,
                "image": item.package.product.image.url if item.package.product.image else None,
                "color": None
            }
            
            # اضافه کردن اطلاعات رنگ اگر وجود داشته باشد
            if hasattr(item.package, 'color') and item.package.color:
                item_data["color"] = {
                    "name": item.package.color.name,
                    "code": item.package.color.hex_code
                }
            
            items_data.append(item_data)
            
        response_data = {
            "items": items_data,
            **order_data
        }
            
        return JsonResponse(response_data)
    except Cart.DoesNotExist:
        return JsonResponse({"error": "سبد خرید پیدا نشد"}, status=404)
    except Exception as e:
        return JsonResponse({"error": f"خطا در دریافت اطلاعات: {str(e)}"}, status=500)


@login_required(login_url='/login/')
def user_notifications(request):
    search = request.GET.get("q")
    if search:
        return redirect(f"/products?q={search}")
    
    # Get common context
    context = get_common_context(request)
    
    # Handle actions for notifications
    if request.method == 'POST':
        if 'mark_read' in request.POST:
            notification_id = request.POST.get('notification_id')
            if notification_id:
                notification = Notification.objects.get(id=notification_id, user=request.user)
                notification.mark_as_read()
                
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({'status': 'success'})
                return redirect('user_notifications')
                
        elif 'mark_all_read' in request.POST:
            Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
            
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'status': 'success'})
            return redirect('user_notifications')
            
        elif 'delete_notification' in request.POST:
            notification_id = request.POST.get('notification_id')
            if notification_id:
                Notification.objects.filter(id=notification_id, user=request.user).delete()
                
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({'status': 'success'})
                return redirect('user_notifications')
    
    return render(request, "frontend/template/notification.html", context)



@login_required(login_url='/login/')
def edit_user_informations(request):
    search = request.GET.get("q")
    if search:
        return redirect(f"/products?q={search}")
    
    # Get common context
    context = get_common_context(request)
    
    if request.method == 'POST':
        user = request.user
        profile = user.profile
        form_type = request.POST.get('form_type')
        
        # Handle the different form types
        if form_type == 'name_form':
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            
            if first_name and last_name:
                user.first_name = first_name
                user.last_name = last_name
                user.save()
                messages.success(request, 'نام و نام خانوادگی با موفقیت به‌روزرسانی شد')
                
        elif form_type == 'national_id_form':
            national_id = request.POST.get('national_id')
            if national_id:
                try:
                    if not validate_iranian_national_id(national_id):
                        messages.error(request, 'کد ملی وارد شده معتبر نیست. کد ملی باید 10 رقم بوده و با الگوریتم صحیح کد ملی مطابقت داشته باشد.')
                    else:
                        profile.national_id = national_id
                        profile.save()
                        messages.success(request, 'کد ملی با موفقیت به‌روزرسانی شد')
                except Exception as e:
                    messages.error(request, f'خطا در به‌روزرسانی کد ملی: {str(e)}')
            elif national_id == '':
                # اگر کاربر فیلد را خالی کرد
                profile.national_id = None
                profile.save()
                messages.success(request, 'کد ملی با موفقیت حذف شد')
                
        elif form_type == 'phone_form':
            phone_number = request.POST.get('phone_number')
            
            if phone_number:
                # Check if the phone number is valid
                if len(phone_number) != 11 or not phone_number.startswith('09'):
                    messages.error(request, 'شماره موبایل باید 11 رقم باشد و با 09 شروع شود')
                else:
                    # Check if the phone number already exists for another user
                    existing_profile = Profile.objects.filter(phone_number=phone_number).exclude(user=user).first()
                    if existing_profile:
                        messages.error(request, 'این شماره موبایل قبلاً برای کاربر دیگری ثبت شده است')
                    else:
                        profile.phone_number = phone_number
                        profile.is_phone_verified = False  # User needs to verify the new phone number
                        profile.save()
                        messages.success(request, 'شماره موبایل با موفقیت به‌روزرسانی شد. لطفاً آن را تأیید کنید')
                
        elif form_type == 'email_form':
            email = request.POST.get('email')
            
            if email:
                # Check if the email already exists for another user
                existing_user = User.objects.filter(email=email).exclude(id=user.id).first()
                if existing_user:
                    messages.error(request, 'این ایمیل قبلاً برای کاربر دیگری ثبت شده است')
                else:
                    user.email = email
                    user.save()
                    messages.success(request, 'ایمیل با موفقیت به‌روزرسانی شد')
                
        elif form_type == 'password_form':
            old_password = request.POST.get('old_password')
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')
            
            if old_password and new_password and confirm_password:
                if user.check_password(old_password):
                    if new_password == confirm_password:
                        user.set_password(new_password)
                        user.save()
                        messages.success(request, 'رمز عبور با موفقیت تغییر کرد')
                        # پس از تغییر رمز عبور، کاربر را دوباره لاگین می‌کنیم
                        from django.contrib.auth import login
                        login(request, user)
                    else:
                        messages.error(request, 'رمز عبور جدید و تکرار آن مطابقت ندارند')
                else:
                    messages.error(request, 'رمز عبور فعلی اشتباه است')
                    
        elif form_type == 'refund_method_form':
            refund_method = request.POST.get('refund_method')
            profile.refund_method = refund_method
            profile.save()
            messages.success(request, 'روش بازگرداندن پول با موفقیت به‌روزرسانی شد')
            
        elif form_type == 'birth_date_form':
            birth_date = request.POST.get('birth_date')
            if birth_date:
                profile.birth_date = birth_date
                profile.save()
                messages.success(request, 'تاریخ تولد با موفقیت به‌روزرسانی شد')
            
        elif form_type == 'job_form':
            job = request.POST.get('job')
            profile.job = job
            profile.save()
            messages.success(request, 'شغل با موفقیت به‌روزرسانی شد')
            
        elif form_type == 'economic_code_form':
            economic_code = request.POST.get('economic_code')
            profile.economic_code = economic_code
            profile.save()
            messages.success(request, 'کد اقتصادی با موفقیت به‌روزرسانی شد')
            
        elif form_type == 'legal_info_form':
            legal_info = request.POST.get('legal_info')
            profile.legal_info = legal_info
            profile.save()
            messages.success(request, 'اطلاعات حقوقی با موفقیت به‌روزرسانی شد')
    
    return render(request, "frontend/template/edit-profile.html", context)


@login_required(login_url='/login/')
def edit_client_address(request):
    # Get common context
    context = get_common_context(request)
    
    # Get only the addresses since other data comes from context processor
    addresses = ClientAddress.objects.filter(user=request.user)
    context['addresses'] = addresses

    update_address = request.POST.get("update_address") == "true"
    create_address = request.POST.get("create_address") == "true"
    delete_address = request.POST.get("delete_address") == "true"
    address_id = request.POST.get("address_id")

    address = None
    if address_id:
        try:
            address = ClientAddress.objects.get(id=address_id, user=request.user)
        except ClientAddress.DoesNotExist:
            address = None

    if request.method == 'POST':
        if update_address and address:
            print(f"[DEBUG] Updating Address: {address}")
            address.title_address = request.POST.get("title_address")
            address.province = request.POST.get('province')
            address.city = request.POST.get('city')
            address.full_address = request.POST.get("full_address")
            address.postcode = request.POST.get('postcode')
            address.save()
            context['success_message'] = "آدرس با موفقیت به‌روزرسانی شد."

        elif create_address:
            print("[DEBUG] Creating New Address")
            ClientAddress.objects.create(
                user=request.user,
                title_address=request.POST.get("title_address"),
                province=request.POST.get('province'),
                city=request.POST.get('city'),
                full_address=request.POST.get("full_address"),
                postcode=request.POST.get('postcode'),
            )
            context['success_message'] = "آدرس جدید با موفقیت اضافه شد."

        elif delete_address and address:
            print(f"[DEBUG] Deleting Address: {address}")
            address.delete()
            context['success_message'] = "آدرس با موفقیت حذف شد."
            return redirect("/profile")

    return render(request, "frontend/template/address.html", context)



@login_required(login_url='/login/')
def liked_list(request):
    # بررسی جستجو
    if request.GET.get('search'):
        return redirect(f"/products?search={request.GET.get('search')}")
    
    # Get common context
    context = get_common_context(request)
    
    # دریافت محصولات مورد علاقه کاربر با اطلاعات کامل
    favourites = FavouriteProducts.objects.filter(user=request.user)
    
    # استخراج محصولات واقعی از آبجکت‌های محبوب با اطلاعات رنگ
    FavouriteProducts = []
    for fav in favourites:
        for product in fav.products.all():
            # دریافت اولین بسته محصول فعال برای رنگ
            package = ProductPackage.objects.filter(product=product, is_active_package=True).first()
            product_data = {
                'id': product.id,
                'name': product.name,
                'price': package.price if package else 0,
                'image': product.image.url if product.image else None,
                'color': {
                    'id': package.color.id if package and package.color else None,
                    'name': package.color.name if package and package.color else None,
                    'code': package.color.hex_code if package and package.color else None,
                } if package and package.color else None,
                'is_available': package.is_active_package if package else False,
            }
            FavouriteProducts.append(product_data)
    
    # اضافه کردن محصولات مورد علاقه به context
    context['FavouriteProducts'] = FavouriteProducts
    
    return render(request, 'frontend/template/favorites.html', context)

@login_required(login_url='/login/')
def add_to_favorites(request):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        product_id = request.POST.get('product_id')
        
        try:
            product = Product.objects.get(id=product_id)
            
            # بررسی وجود یا ایجاد آبجکت FavouriteProducts برای کاربر
            fav_obj, created = FavouriteProducts.objects.get_or_create(user=request.user)
            
            # اضافه کردن محصول به لیست علاقه‌مندی‌ها
            if product not in fav_obj.products.all():
                fav_obj.products.add(product)
                return JsonResponse({'status': 'success', 'message': 'محصول به لیست علاقه‌مندی‌ها اضافه شد'})
            else:
                return JsonResponse({'status': 'info', 'message': 'این محصول قبلاً در لیست علاقه‌مندی‌ها وجود دارد'})
                
        except Product.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'محصول یافت نشد'}, status=404)
    
    return JsonResponse({'status': 'error', 'message': 'درخواست نامعتبر'}, status=400)

@require_POST
@login_required
def remove_from_favorites(request):
    product_id = request.POST.get('product_id')
    if not product_id:
        return JsonResponse({'status': 'error', 'message': 'شناسه محصول مشخص نشده است'})
        
    try:
        product = Product.objects.get(id=product_id)
        favorite = FavouriteProducts.objects.filter(user=request.user, products=product)
        if favorite.exists():
            # حذف محصول از لیست محبوب‌ها
            for fav in favorite:
                fav.products.remove(product)
            return JsonResponse({'status': 'success', 'message': 'محصول از لیست علاقه‌مندی‌ها حذف شد'})
        else:
            return JsonResponse({'status': 'error', 'message': 'این محصول در لیست علاقه‌مندی‌های شما نیست'})
    except Product.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'محصول مورد نظر یافت نشد'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'خطا: {str(e)}'})

@login_required(login_url='/login/')
def user_comments(request):
    # Check if there's a search query
    if request.GET.get('search'):
        return redirect(f"/products?search={request.GET.get('search')}")
    
    # Get common context
    context = get_common_context(request)
    
    return render(request, 'frontend/template/user_comments.html', context)

def get_common_context(request):
    """
    جمع‌آوری اطلاعات مشترک برای همه view ها
    این تابع تمام اطلاعات پایه مورد نیاز برای نمایش در صفحات مختلف پنل کاربری را برمی‌گرداند
    """
    # بررسی اینکه آیا کاربر احراز هویت شده است
    if not request.user.is_authenticated:
        return {}  # اگر کاربر لاگین نیست، دیکشنری خالی برگردان
    
    # Get user's notifications
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    notifications_count = notifications.filter(is_read=False).count()
    
    # Get user's comments
    comments = Comment.objects.filter(user=request.user)
    comments_count = len(comments)
    
    # Get user's cart information
    cart = Cart.objects.filter(user=request.user, is_paid=False).first()
    cart_info = get_cart_info(cart)
    
    # Get last 10 orders for the user
    orders = Order.objects.filter(user=request.user).order_by('-order_date')[:10]
    all_orders_count = Order.objects.filter(user=request.user).count()
    
    # Count user's favorite products
    fav_products = FavouriteProducts.objects.filter(user=request.user)
    FavouriteProducts_count = fav_products.count()
    
    # Categorize orders by status and payment status
    orders_pending = []
    orders_confirmed = []
    orders_shipped = []
    orders_delivered = []
    orders_canceled = []
    orders_paid = []
    orders_unpaid = []

    for order in orders:
        # دسته‌بندی بر اساس وضعیت سفارش
        if order.status == "در حال انتظار":
            orders_pending.append(order)
        elif order.status == "تأیید شده":
            orders_confirmed.append(order)
        elif order.status == "ارسال شده":
            orders_shipped.append(order)
        elif order.status == "تحویل داده شده":
            orders_delivered.append(order)
        elif order.status == "لغو شده":
            orders_canceled.append(order)
        
        # دسته‌بندی بر اساس وضعیت پرداخت
        if order.payment_status == "پرداخت شده":
            orders_paid.append(order)
        elif order.payment_status == "در انتظار پرداخت" or order.payment_status == "ناموفق" or order.payment_status == "لغو شده":
            orders_unpaid.append(order)
    
    return {
        # User basic information
        'username': request.user.username,
        'email': request.user.email,
        'first_name': request.user.first_name,
        'last_name': request.user.last_name,
        
        # Notifications
        'notifications': notifications,
        'notifications_count': notifications_count,
        
        # Comments
        'comments': comments,
        'comments_count': comments_count,
        
        # Cart information
        'cart_items': cart_info['cart_items'],
        'cart_count': sum(item['count'] for item in cart_info['cart_items']),
        'cart_total': cart_info['cart_total'],
        
        # All orders and their status counts
        'orders': orders,
        'all_orders_count': all_orders_count,
        'orders_pending': orders_pending,
        'orders_confirmed': orders_confirmed,
        'orders_shipped': orders_shipped,
        'orders_delivered': orders_delivered,
        'orders_canceled': orders_canceled,
        'orders_pending_count': len(orders_pending),
        'orders_confirmed_count': len(orders_confirmed),
        'orders_shipped_count': len(orders_shipped),
        'orders_delivered_count': len(orders_delivered),
        'orders_canceled_count': len(orders_canceled),
        
        # Payment status information
        'orders_paid': orders_paid,
        'orders_unpaid': orders_unpaid,
        'orders_paid_count': len(orders_paid),
        'orders_unpaid_count': len(orders_unpaid),
        
        # Favorites
        'FavouriteProducts_count': FavouriteProducts_count,
    }

def reset_password_request(request):
    """
    View for requesting a password reset
    Sends a verification code to the provided phone number
    """
    if request.method == 'POST':
        phone_number = request.POST.get('phone_number', '').strip()
        
        # Validate phone number
        if not phone_number or len(phone_number) != 11 or not phone_number.startswith('09'):
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'error',
                    'message': 'شماره موبایل نامعتبر است'
                })
            messages.error(request, 'شماره موبایل نامعتبر است')
            return redirect('login')
        
        # Check if user with this phone number exists in the Profile model
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        try:
            # Look up the profile with this phone number
            profile = Profile.objects.get(phone_number=phone_number)
            user = profile.user  # Get the associated user
        except Profile.DoesNotExist:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'error',
                    'message': 'کاربری با این شماره موبایل یافت نشد'
                })
            messages.error(request, 'کاربری با این شماره موبایل یافت نشد')
            return redirect('login')
        
        # Generate verification code using your existing utility
        from utils.sms import generate_verification_code, send_verification_sms
        verification_code = generate_verification_code()
        
        # Store verification code in the session with a timestamp
        import datetime
        request.session['reset_verification'] = {
            'phone_number': phone_number,
            'code': verification_code,
            'timestamp': datetime.datetime.now().timestamp(),
            'attempts': 0,
            'user_id': user.id  # Store user ID for later use
        }
        request.session.save()
        
        # Send SMS with verification code using your existing utility
        success, response = send_verification_sms(phone_number, verification_code)
        
        if not success:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'error',
                    'message': f'خطا در ارسال پیامک: {response}'
                })
            messages.error(request, f'خطا در ارسال پیامک: {response}')
            return redirect('login')
        
        # For development/debugging
        print(f"Password reset code for {phone_number}: {verification_code}")
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'success',
                'message': 'کد تایید به شماره موبایل شما ارسال شد'
            })
        
        messages.success(request, 'کد تایید به شماره موبایل شما ارسال شد')
        return redirect('login')
    
    # If GET request, redirect to login page
    return redirect('login')

def verify_reset_code(request):
    """
    Verify the reset code entered by the user
    """
    if request.method == 'POST':
        phone_number = request.POST.get('phone_number', '').strip()
        verification_code = request.POST.get('verification_code', '').strip()
        
        # Get verification data from session
        reset_data = request.session.get('reset_verification', {})
        
        # Check if verification data exists and matches the provided information
        if not reset_data or reset_data.get('phone_number') != phone_number:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'error',
                    'message': 'اطلاعات بازیابی رمز عبور نامعتبر است. لطفاً دوباره درخواست دهید'
                })
            messages.error(request, 'اطلاعات بازیابی رمز عبور نامعتبر است. لطفاً دوباره درخواست دهید')
            return redirect('login')
        
        # Check if code has expired using your utility function
        from datetime import datetime
        from utils.sms import is_verification_code_expired
        
        timestamp = reset_data.get('timestamp', 0)
        code_created_at = datetime.fromtimestamp(timestamp)
        
        if is_verification_code_expired(code_created_at):
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'error',
                    'message': 'کد تایید منقضی شده است. لطفاً دوباره درخواست دهید'
                })
            messages.error(request, 'کد تایید منقضی شده است. لطفاً دوباره درخواست دهید')
            return redirect('login')
        
        # Increment attempt counter and check if max attempts reached
        attempts = reset_data.get('attempts', 0) + 1
        reset_data['attempts'] = attempts
        request.session['reset_verification'] = reset_data
        request.session.save()
        
        if attempts > 3:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'error',
                    'message': 'تعداد تلاش‌های ناموفق بیش از حد مجاز است. لطفاً دوباره درخواست دهید'
                })
            messages.error(request, 'تعداد تلاش‌های ناموفق بیش از حد مجاز است. لطفاً دوباره درخواست دهید')
            return redirect('login')
        
        # Verify the code
        if reset_data.get('code') != verification_code:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'error',
                    'message': 'کد تایید نادرست است'
                })
            messages.error(request, 'کد تایید نادرست است')
            return redirect('login')
        
        # Generate a secure reset token
        import uuid
        import hashlib
        reset_token = hashlib.sha256(f"{phone_number}:{uuid.uuid4()}".encode()).hexdigest()
        
        # Store reset token in session
        reset_data['reset_token'] = reset_token
        reset_data['token_timestamp'] = datetime.now().timestamp()
        request.session['reset_verification'] = reset_data
        request.session.save()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'success',
                'message': 'کد تایید صحیح است',
                'reset_token': reset_token
            })
        
        messages.success(request, 'کد تایید صحیح است. لطفاً رمز عبور جدید را وارد کنید')
        return redirect('login')
    
    # If GET request, redirect to login page
    return redirect('login')

def set_new_password(request):
    """
    Set a new password for the user after verification
    """
    if request.method == 'POST':
        reset_token = request.POST.get('reset_token', '').strip()
        new_password = request.POST.get('new_password', '').strip()
        confirm_password = request.POST.get('confirm_new_password', '').strip()
        
        # Get verification data from session
        reset_data = request.session.get('reset_verification', {})
        
        # Validate reset token
        if not reset_data or reset_data.get('reset_token') != reset_token:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'error',
                    'message': 'توکن بازیابی رمز عبور نامعتبر است'
                })
            messages.error(request, 'توکن بازیابی رمز عبور نامعتبر است')
            return redirect('login')
        
        # Check if token has expired (10 minutes = 600 seconds)
        import datetime
        token_timestamp = reset_data.get('token_timestamp', 0)
        current_time = datetime.datetime.now().timestamp()
        
        if current_time - token_timestamp > 600:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'error',
                    'message': 'توکن بازیابی رمز عبور منقضی شده است. لطفاً دوباره درخواست دهید'
                })
            messages.error(request, 'توکن بازیابی رمز عبور منقضی شده است. لطفاً دوباره درخواست دهید')
            return redirect('login')
        
        # Validate password
        if not new_password or len(new_password) < 8:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'error',
                    'message': 'رمز عبور باید حداقل 8 کاراکتر باشد'
                })
            messages.error(request, 'رمز عبور باید حداقل 8 کاراکتر باشد')
            return redirect('login')
        
        if new_password != confirm_password:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'error',
                    'message': 'رمز عبور و تکرار آن مطابقت ندارند'
                })
            messages.error(request, 'رمز عبور و تکرار آن مطابقت ندارند')
            return redirect('login')
        
        # Get the user by ID and update password
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        try:
            user_id = reset_data.get('user_id')
            if not user_id:
                raise User.DoesNotExist
                
            user = User.objects.get(id=user_id)
            user.set_password(new_password)
            user.save()
            
            # Clear reset data from session
            if 'reset_verification' in request.session:
                del request.session['reset_verification']
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'success',
                    'message': 'رمز عبور با موفقیت تغییر یافت'
                })
            
            messages.success(request, 'رمز عبور با موفقیت تغییر یافت. اکنون می‌توانید وارد شوید')
            return redirect('login')
        
        except User.DoesNotExist:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'error',
                    'message': 'کاربر مورد نظر یافت نشد'
                })
            messages.error(request, 'کاربر مورد نظر یافت نشد')
            return redirect('login')
        
        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'error',
                    'message': f'خطا در تغییر رمز عبور: {str(e)}'
                })
            messages.error(request, f'خطا در تغییر رمز عبور: {str(e)}')
            return redirect('login')
    
    # If GET request, redirect to login page
    return redirect('login')

@login_required(login_url='/login/')
def user_offers(request):
    coupons = UserCoupon.objects.filter(user=request.user)
    context = {
        'coupons': coupons,
    }
    return render(request, 'frontend/template/offers.html', context)

