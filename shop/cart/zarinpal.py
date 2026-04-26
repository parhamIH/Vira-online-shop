import requests
import json
import logging

# تنظیم لاگینگ برای دیباگ بهتر
logger = logging.getLogger(__name__)

class ZarinPal:
    """
    کلاس اتصال به درگاه پرداخت زرین‌پال
    نسخه به‌روزشده با آخرین API زرین‌پال
    """
    def __init__(self, merchant_id, callback_url, sandbox=False):
        self.merchant_id = merchant_id
        self.callback_url = callback_url
        self.sandbox = sandbox
        
        # print(f"Initializing ZarinPal with merchant_id: {merchant_id}, sandbox: {sandbox}")
        # print(f"Callback URL: {callback_url}")
        
        # آدرس‌های API زرین‌پال - نسخه جدید
        if sandbox:
            # آدرس‌های محیط تست
            self.domain = "sandbox"
            # آدرس درخواست پرداخت - استاندارد قدیمی (rest)
            self.payment_request_url = 'https://sandbox.zarinpal.com/pg/rest/WebGate/PaymentRequest.json'
            # آدرس درخواست پرداخت - استاندارد جدید (v4)
            self.payment_request_v4_url = 'https://sandbox.zarinpal.com/pg/v4/payment/request.json'
            # آدرس درگاه پرداخت
            self.payment_gateway_url = 'https://sandbox.zarinpal.com/pg/StartPay/'
            self.payment_gateway_authority_url = 'https://sandbox.zarinpal.com/pg/StartPay/{authority}'
            # آدرس تایید پرداخت - استاندارد قدیمی (rest)
            self.verification_url = 'https://sandbox.zarinpal.com/pg/rest/WebGate/PaymentVerification.json'
            # آدرس تایید پرداخت - استاندارد جدید (v4)
            self.verification_v4_url = 'https://sandbox.zarinpal.com/pg/v4/payment/verify.json'
        else:
            # آدرس‌های محیط واقعی
            self.domain = "www"
            # آدرس درخواست پرداخت - استاندارد قدیمی (rest)
            self.payment_request_url = 'https://api.zarinpal.com/pg/rest/WebGate/PaymentRequest.json'
            # آدرس درخواست پرداخت - استاندارد جدید (v4)
            self.payment_request_v4_url = 'https://api.zarinpal.com/pg/v4/payment/request.json'
            # آدرس درگاه پرداخت
            self.payment_gateway_url = 'https://www.zarinpal.com/pg/StartPay/'
            self.payment_gateway_authority_url = 'https://www.zarinpal.com/pg/StartPay/{authority}'
            # آدرس تایید پرداخت - استاندارد قدیمی (rest)
            self.verification_url = 'https://api.zarinpal.com/pg/rest/WebGate/PaymentVerification.json'
            # آدرس تایید پرداخت - استاندارد جدید (v4)
            self.verification_v4_url = 'https://api.zarinpal.com/pg/v4/payment/verify.json'
            
        # print(f"Payment request URL (old): {self.payment_request_url}")
        # print(f"Payment request URL (new): {self.payment_request_v4_url}")
        # print(f"Payment gateway URL: {self.payment_gateway_url}")
        # print(f"Verification URL (old): {self.verification_url}")
        # print(f"Verification URL (new): {self.verification_v4_url}")
    
    def payment_request(self, amount, description, email=None, mobile=None):
        """
        ارسال درخواست تراکنش و دریافت توکن برای هدایت به درگاه پرداخت
        """
        # تبدیل قیمت به ریال (زرین پال از ریال استفاده می کند)
        amount_in_rials = amount * 10
        
        # print(f"Requesting payment - Amount: {amount} Toman ({amount_in_rials} Rial)")
        
        # اول با استاندارد جدید تلاش می‌کنیم
        result = self._payment_request_new_api(amount_in_rials, description, email, mobile)
        
        # اگر موفق نبود، با استاندارد قدیمی تلاش می‌کنیم
        if not result['success']:
            # print("New API failed, trying old API...")
            result = self._payment_request_old_api(amount_in_rials, description, email, mobile)
            
        # چک نهایی نتیجه
        if result['success'] and 'authority' in result:
            # ساخت URL کامل با استفاده از مقدار authority
            authority = result['authority']
            # ساخت URL درگاه پرداخت
            payment_url = f"{self.payment_gateway_url}{authority}"
            
            # print(f"Generated payment URL: {payment_url}")
            result['url'] = payment_url
            
            # در محیط تست اگر URL کار نکرد، URL پشتیبان را امتحان کنیم
            if self.sandbox:
                alternative_url = f"https://{self.domain}.zarinpal.com/pg/StartPay/{authority}"
                if payment_url != alternative_url:
                    # print(f"In sandbox mode, adding alternative URL: {alternative_url}")
                    result['alternative_url'] = alternative_url
            
        return result
    
    def _payment_request_old_api(self, amount_in_rials, description, email=None, mobile=None):
        """
        ارسال درخواست پرداخت با استفاده از API قدیمی زرین‌پال
        """
        # ساخت داده برای ارسال به درگاه
        data = {
            'MerchantID': self.merchant_id,
            'Amount': amount_in_rials,
            'Description': description,
            'CallbackURL': self.callback_url,
        }
        
        if email:
            data['Email'] = email
            
        if mobile:
            data['Mobile'] = mobile
        
        # print(f"Old API request URL: {self.payment_request_url}")
        # print(f"Old API request data: {data}")
            
        # ارسال درخواست به زرین پال
        try:
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
            response = requests.post(self.payment_request_url, json=data, headers=headers, timeout=10)
            # print(f"Old API response status: {response.status_code}")
            # print(f"Old API response content: {response.text}")
            
            # بررسی کد وضعیت HTTP
            if response.status_code != 200:
                return {
                    'success': False, 
                    'error': f'خطای HTTP: {response.status_code}', 
                    'status': response.status_code
                }
            
            response_data = response.json()
            
            # بررسی پاسخ
            if response_data.get('Status') == 100:
                # درخواست موفق - دریافت توکن و ساخت URL
                authority = response_data.get('Authority')
                # اطمینان از معتبر بودن شناسه
                if not authority:
                    # print("Error: Empty authority received from ZarinPal")
                    return {'success': False, 'error': 'شناسه پرداخت دریافت نشد', 'status': -99}
                    
                # print(f"Old API success - Authority: {authority}")
                return {'success': True, 'authority': authority}
            else:
                # درخواست ناموفق
                status_code = response_data.get('Status')
                error_message = self._get_error_message(status_code)
                # print(f"Old API payment request failed with status {status_code}: {error_message}")
                return {'success': False, 'error': error_message, 'status': status_code}
                
        except requests.exceptions.RequestException as e:
            # print(f"Old API connection error: {str(e)}")
            return {'success': False, 'error': f'خطا در اتصال به درگاه: {str(e)}'}
        except (ValueError, json.JSONDecodeError) as e:
            # print(f"Old API response parsing error: {str(e)}")
            return {'success': False, 'error': f'خطا در فرمت پاسخ درگاه: {str(e)}'}
        except Exception as e:
            # print(f"Old API unexpected error: {str(e)}")
            return {'success': False, 'error': f'خطای نامشخص: {str(e)}'}
            
    def _payment_request_new_api(self, amount_in_rials, description, email=None, mobile=None):
        """
        ارسال درخواست پرداخت با استفاده از API جدید زرین‌پال (v4)
        """
        # ساخت داده برای ارسال به درگاه
        data = {
            'merchant_id': self.merchant_id,
            'amount': amount_in_rials,
            'description': description,
            'callback_url': self.callback_url,
            'metadata': {}
        }
        
        if email:
            data['metadata']['email'] = email
            
        if mobile:
            data['metadata']['mobile'] = mobile
        
        # print(f"New API request URL: {self.payment_request_v4_url}")
        # print(f"New API request data: {data}")
            
        # ارسال درخواست به زرین پال
        try:
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
            response = requests.post(self.payment_request_v4_url, json=data, headers=headers, timeout=10)
            # print(f"New API response status: {response.status_code}")
            # print(f"New API response content: {response.text}")
            
            # بررسی کد وضعیت HTTP
            if response.status_code != 200:
                return {
                    'success': False, 
                    'error': f'خطای HTTP: {response.status_code}', 
                    'status': response.status_code
                }
            
            response_data = response.json()
            
            # بررسی پاسخ در API جدید
            if response_data.get('data', {}).get('code') == 100:
                # درخواست موفق - دریافت توکن
                authority = response_data.get('data', {}).get('authority')
                if not authority:
                    # print("Error: Empty authority received from ZarinPal")
                    return {'success': False, 'error': 'شناسه پرداخت دریافت نشد', 'status': -99}
                
                # print(f"New API success - Authority: {authority}")
                return {'success': True, 'authority': authority}
            else:
                # درخواست ناموفق
                errors = response_data.get('errors', [])
                error_message = errors[0].get('message') if errors else 'خطای نامشخص'
                code = errors[0].get('code') if errors else -1
                # print(f"New API payment request failed with code {code}: {error_message}")
                return {'success': False, 'error': error_message, 'status': code}
                
        except requests.exceptions.RequestException as e:
            # print(f"New API connection error: {str(e)}")
            return {'success': False, 'error': f'خطا در اتصال به درگاه: {str(e)}'}
        except (ValueError, json.JSONDecodeError) as e:
            # print(f"New API response parsing error: {str(e)}")
            return {'success': False, 'error': f'خطا در فرمت پاسخ درگاه: {str(e)}'}
        except Exception as e:
            # print(f"New API unexpected error: {str(e)}")
            return {'success': False, 'error': f'خطای نامشخص: {str(e)}'}
    
    def payment_verification(self, authority, amount):
        """
        تأیید تراکنش و دریافت کد پیگیری
        """
        # تبدیل قیمت به ریال
        amount_in_rials = amount * 10
        
        # print(f"Verifying payment - Authority: {authority}, Amount: {amount} Toman ({amount_in_rials} Rial)")
        
        # اول با استاندارد جدید تلاش می‌کنیم
        result = self._payment_verification_new_api(authority, amount_in_rials)
        
        # اگر موفق نبود، با استاندارد قدیمی تلاش می‌کنیم
        if not result['success']:
            # print("New API verification failed, trying old API...")
            result = self._payment_verification_old_api(authority, amount_in_rials)
            
        return result
    
    def _payment_verification_old_api(self, authority, amount_in_rials):
        """
        تأیید تراکنش با استفاده از API قدیمی زرین‌پال
        """
        # ساخت داده برای ارسال به درگاه
        data = {
            'MerchantID': self.merchant_id,
            'Authority': authority,
            'Amount': amount_in_rials,
        }
        
        # print(f"Old API verification URL: {self.verification_url}")
        # print(f"Old API verification data: {data}")
            
        # ارسال درخواست تأیید به زرین پال
        try:
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
            response = requests.post(self.verification_url, json=data, headers=headers, timeout=10)
            # print(f"Old API verification response status: {response.status_code}")
            # print(f"Old API verification response content: {response.text}")
            
            # بررسی کد وضعیت HTTP
            if response.status_code != 200:
                return {
                    'success': False, 
                    'error': f'خطای HTTP: {response.status_code}', 
                    'status': response.status_code
                }
            
            response_data = response.json()
            
            # بررسی پاسخ
            if response_data.get('Status') == 100:
                # تأیید موفق - دریافت کد پیگیری
                ref_id = response_data.get('RefID')
                # print(f"Old API verification success - RefID: {ref_id}")
                return {'success': True, 'ref_id': ref_id}
            else:
                # تأیید ناموفق
                status_code = response_data.get('Status')
                error_message = self._get_error_message(status_code)
                # print(f"Old API verification failed with status {status_code}: {error_message}")
                return {'success': False, 'error': error_message, 'status': status_code}
                
        except requests.exceptions.RequestException as e:
            # print(f"Old API verification connection error: {str(e)}")
            return {'success': False, 'error': f'خطا در اتصال به درگاه: {str(e)}'}
        except (ValueError, json.JSONDecodeError) as e:
            # print(f"Old API verification response parsing error: {str(e)}")
            return {'success': False, 'error': f'خطا در فرمت پاسخ درگاه: {str(e)}'}
        except Exception as e:
            # print(f"Old API verification unexpected error: {str(e)}")
            return {'success': False, 'error': f'خطای نامشخص: {str(e)}'}
            
    def _payment_verification_new_api(self, authority, amount_in_rials):
        """
        تأیید تراکنش با استفاده از API جدید زرین‌پال (v4)
        """
        # ساخت داده برای ارسال به درگاه
        data = {
            'merchant_id': self.merchant_id,
            'authority': authority,
            'amount': amount_in_rials,
        }
        
        # print(f"New API verification URL: {self.verification_v4_url}")
        # print(f"New API verification data: {data}")
            
        # ارسال درخواست تأیید به زرین پال
        try:
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
            response = requests.post(self.verification_v4_url, json=data, headers=headers, timeout=10)
            # print(f"New API verification response status: {response.status_code}")
            # print(f"New API verification response content: {response.text}")
            
            # بررسی کد وضعیت HTTP
            if response.status_code != 200:
                return {
                    'success': False, 
                    'error': f'خطای HTTP: {response.status_code}', 
                    'status': response.status_code
                }
            
            response_data = response.json()
            
            # بررسی پاسخ در API جدید
            if response_data.get('data', {}).get('code') == 100:
                # تأیید موفق - دریافت کد پیگیری
                ref_id = response_data.get('data', {}).get('ref_id')
                if not ref_id:
                    # print("Error: Empty ref_id received from ZarinPal")
                    return {'success': False, 'error': 'کد پیگیری دریافت نشد', 'status': -99}
                
                # print(f"New API verification success - RefID: {ref_id}")
                return {'success': True, 'ref_id': ref_id}
            else:
                # تأیید ناموفق
                errors = response_data.get('errors', [])
                error_message = errors[0].get('message') if errors else 'خطای نامشخص'
                code = errors[0].get('code') if errors else -1
                # print(f"New API verification failed with code {code}: {error_message}")
                return {'success': False, 'error': error_message, 'status': code}
                
        except requests.exceptions.RequestException as e:
            # print(f"New API verification connection error: {str(e)}")
            return {'success': False, 'error': f'خطا در اتصال به درگاه: {str(e)}'}
        except (ValueError, json.JSONDecodeError) as e:
            # print(f"New API verification response parsing error: {str(e)}")
            return {'success': False, 'error': f'خطا در فرمت پاسخ درگاه: {str(e)}'}
        except Exception as e:
            # print(f"New API verification unexpected error: {str(e)}")
            return {'success': False, 'error': f'خطای نامشخص: {str(e)}'}
    
    def _get_error_message(self, status_code):
        """
        دریافت پیام خطا بر اساس کد وضعیت زرین‌پال
        """
        error_codes = {
            -1: 'اطلاعات ارسال شده ناقص است',
            -2: 'آی پی یا مرچنت کد پذیرنده صحیح نیست',
            -3: 'با توجه به محدودیت‌های شاپرک، امکان پرداخت با رقم درخواست شده میسر نیست',
            -4: 'سطح تأیید پذیرنده پایین‌تر از سطح نقره‌ای است',
            -11: 'درخواست مورد نظر یافت نشد',
            -12: 'امکان ویرایش درخواست میسر نیست',
            -21: 'هیچ نوع عملیات مالی برای این تراکنش یافت نشد',
            -22: 'تراکنش ناموفق می‌باشد',
            -33: 'رقم تراکنش با رقم پرداخت شده مطابقت ندارد',
            -34: 'سقف تقسیم تراکنش از لحاظ تعداد یا رقم عبور نموده است',
            -40: 'اجازه دسترسی به متد مربوطه وجود ندارد',
            -41: 'اطلاعات ارسال شده مربوط به AdditionalData غیرمعتبر می‌باشد',
            -42: 'مدت زمان معتبر طول عمر شناسه پرداخت باید بین ۳۰ دقیقه تا ۴۵ روز باشد',
            -54: 'درخواست مورد نظر آرشیو شده است',
            100: 'عملیات با موفقیت انجام شد',
            101: 'عملیات پرداخت با موفقیت انجام شده ولی قبلا عملیات تأیید روی این تراکنش انجام شده است',
        }
        
        # برگرداندن پیام خطا بر اساس کد وضعیت
        return error_codes.get(status_code, f'خطای ناشناخته کد {status_code}') 