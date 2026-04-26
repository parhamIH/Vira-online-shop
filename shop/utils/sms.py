from kavenegar import *
import os
import random
import string
from datetime import datetime, timedelta
from django.utils import timezone

# کلید API کاوه نگار را از متغیرهای محیطی می‌خوانیم یا به صورت مستقیم تعریف می‌کنیم
KAVENEGAR_API_KEY = os.environ.get('KAVENEGAR_API_KEY', '')
KAVENEGAR_SENDER = '2000660110'  # شماره ارسال کننده پیامک

def generate_verification_code():
    """تولید کد تصادفی 6 رقمی برای تأیید شماره تلفن"""
    return ''.join(random.choices(string.digits, k=6))

def send_verification_sms(phone_number, code):
    """ارسال پیامک حاوی کد تأیید به شماره تلفن کاربر"""
    try:
        api = KavenegarAPI(KAVENEGAR_API_KEY)
        params = {
            'receptor': phone_number,
            'sender': KAVENEGAR_SENDER,
            'message': f"کد تایید شما: {code} \n fatiima_accessories \n  instagram :https://www.instagram.com/fatiima_accessories/ ",  # فقط کد تأیید را ارسال می‌کنیم
            'type': 'sms'
        }
        response = api.sms_send(params)
        print(f"SMS sent to {phone_number} with code {code}")
        return True, response
    except APIException as e:
        print(f"API Exception: {str(e)}")
        return False, str(e)
    except HTTPException as e:
        print(f"HTTP Exception: {str(e)}")
        return False, str(e)
    except Exception as e:
        print(f"General Exception: {str(e)}")
        return False, str(e)

def is_verification_code_expired(created_at, expiry_minutes=2):
    """بررسی انقضای کد تأیید بر اساس زمان ایجاد"""
    if not created_at:
        return True
    
    # اطمینان از اینکه هر دو زمان دارای timezone باشند
    now = timezone.now()
    if created_at.tzinfo is None:
        created_at = timezone.make_aware(created_at)
    
    # زمان انقضا را محاسبه می‌کنیم
    expiry_time = created_at + timedelta(minutes=expiry_minutes)
    
    # مقایسه با زمان فعلی
    return now > expiry_time 

def send_sms(phone_number, message):
    """ارسال پیامک دلخواه به شماره تلفن کاربر"""
    try:
        api = KavenegarAPI(KAVENEGAR_API_KEY)
        params = {
            'receptor': phone_number,
            'sender': KAVENEGAR_SENDER,
            'message': message,
            'type': 'sms'
        }
        response = api.sms_send(params)
        print(f"SMS sent to {phone_number}: {message}")
        return True, response
    except APIException as e:
        print(f"API Exception: {str(e)}")
        return False, str(e)
    except HTTPException as e:
        print(f"HTTP Exception: {str(e)}")
        return False, str(e)
    except Exception as e:
        print(f"General Exception: {str(e)}")
        return False, str(e) 
