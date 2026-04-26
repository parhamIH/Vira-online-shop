"""
اسکریپت تست اتصال به درگاه زرین‌پال
این اسکریپت را می‌توانید به صورت مستقل اجرا کنید تا اتصال به درگاه زرین‌پال را تست کنید

برای اجرا، از ترمینال به پوشه پروژه بروید و دستور زیر را اجرا کنید:
python -m cart.zarinpal_test

این اسکریپت تمام فرآیند ارتباط با زرین‌پال را شبیه‌سازی می‌کند.
"""

import sys
import time
import os

# تلاش برای import به روش‌های مختلف
try:
    # روش اول: import نسبی (وقتی به صورت ماژول اجرا می‌شود)
    from .zarinpal import ZarinPal
except ImportError:
    try:
        # روش دوم: import با نام کامل ماژول
        from cart.zarinpal import ZarinPal
    except ImportError:
        # روش سوم: import محلی (وقتی در همان دایرکتوری هستیم)
        import os
        import sys
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from zarinpal import ZarinPal

# تنظیمات زرین‌پال
MERCHANT_ID = 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx'  # مرچنت آی دی تست
CALLBACK_URL = 'http://localhost:8000/verify-payment/'
SANDBOX = True  # استفاده از محیط تست

def test_zarinpal_connection():
    """
    تست اتصال و درخواست پرداخت به زرین‌پال
    """
    print("=== تست اتصال به درگاه زرین‌پال ===")
    print(f"Merchant ID: {MERCHANT_ID}")
    print(f"Callback URL: {CALLBACK_URL}")
    print(f"Sandbox mode: {SANDBOX}")
    
    # ایجاد نمونه از کلاس ZarinPal
    try:
        client = ZarinPal(MERCHANT_ID, CALLBACK_URL, sandbox=SANDBOX)
        print("\n✅ ایجاد نمونه از کلاس ZarinPal با موفقیت انجام شد")
    except Exception as e:
        print(f"\n❌ خطا در ایجاد نمونه از کلاس ZarinPal: {e}")
        return
    
    # درخواست پرداخت تست
    amount = 1000  # مبلغ به تومان
    description = 'تست اتصال به درگاه زرین‌پال'
    email = 'test@example.com'  # اختیاری
    
    print("\n=== ارسال درخواست پرداخت ===")
    print(f"Amount: {amount} Toman")
    print(f"Description: {description}")
    
    try:
        result = client.payment_request(amount, description, email=email)
        print(f"\n✅ درخواست پرداخت ارسال شد")
        print(f"Result: {result}")
    except Exception as e:
        print(f"\n❌ خطا در ارسال درخواست پرداخت: {e}")
        return
    
    # بررسی نتیجه
    if result.get('success', False):
        authority = result.get('authority', '')
        payment_url = result.get('url', '')
        print(f"\n✅ درخواست پرداخت موفقیت‌آمیز بود")
        print(f"Authority: {authority}")
        print(f"Payment URL: {payment_url}")
        
        # نمایش لینک پرداخت برای تست دستی
        print("\nبرای تست دستی پرداخت، می‌توانید لینک زیر را در مرورگر خود باز کنید:")
        print(payment_url)
        
        # شبیه‌سازی تأیید پرداخت
        print("\n=== شبیه‌سازی تأیید پرداخت ===")
        print("در یک سناریوی واقعی، کاربر پس از پرداخت در درگاه زرین‌پال،")
        print("به آدرس callback_url هدایت می‌شود و سپس عملیات تأیید پرداخت انجام می‌شود.")
        
        # در اینجا می‌توانید از کاربر بپرسید که آیا میخواهد تأیید پرداخت را تست کند
        verify = input("\nآیا می‌خواهید تأیید پرداخت را تست کنید؟ (y/n): ")
        if verify.lower() == 'y':
            # استفاده از همان authority برای تست تأیید پرداخت
            print("\n=== تست تأیید پرداخت ===")
            
            try:
                verification_result = client.payment_verification(authority, amount)
                print(f"✅ درخواست تأیید پرداخت ارسال شد")
                print(f"Result: {verification_result}")
            except Exception as e:
                print(f"❌ خطا در ارسال درخواست تأیید پرداخت: {e}")
                return
            
            if verification_result.get('success', False):
                ref_id = verification_result.get('ref_id', '')
                print(f"\n✅ تأیید پرداخت موفقیت‌آمیز بود")
                print(f"Reference ID: {ref_id}")
            else:
                error = verification_result.get('error', 'Unknown error')
                print(f"\n❌ تأیید پرداخت ناموفق بود: {error}")
        else:
            print("\nتأیید پرداخت تست نشد.")
    else:
        error = result.get('error', 'Unknown error')
        print(f"\n❌ درخواست پرداخت ناموفق بود: {error}")
    
    print("\n=== اتمام تست ===")
    return result.get('success', False)

if __name__ == "__main__":
    # اگر از جنگو اجرا می‌شود، محیط جنگو را تنظیم می‌کنیم
    if 'DJANGO_SETTINGS_MODULE' not in os.environ:
        # تنظیم محیط جنگو
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_dir = os.path.dirname(current_dir)
        sys.path.append(project_dir)
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')
        
        try:
            import django
            django.setup()
            print("Django environment setup successfully.")
        except ImportError:
            print("Django could not be imported. Test will run without Django.")
    
    # اجرای تست
    success = test_zarinpal_connection()
    
    # خروج با کد مناسب
    if not success:
        print("\n⚠️ تست با خطا مواجه شد")
        sys.exit(1)
    else:
        sys.exit(0) 