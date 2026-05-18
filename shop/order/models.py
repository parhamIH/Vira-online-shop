from django.db import models
from model_utils import FieldTracker  # Add this import
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from shop.cart.models import Cart
import uuid

# Create your models here.
#__________________________________________ ------Order------ _______________________________________
class Order(models.Model):
    SHIPPING_CHOICES = [
        ('post', 'پست'),
        ('tipax', 'تیپاکس'),
        ('express', 'پیک موتوری'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    cart = models.OneToOneField('cart.Cart', on_delete=models.PROTECT)
    address = models.ForeignKey('account.ClientAddress', on_delete=models.PROTECT)
    
    order_number = models.CharField(max_length=100, unique=True, editable=False, default=uuid.uuid4)
    order_date = models.DateTimeField(auto_now_add=True)
    payment_method = models.CharField(max_length=50, choices=[
        ('online', 'پرداخت آنلاین'),
        ('wallet', 'کیف پول'),
        ('cod', 'پرداخت در محل'),
    ])
    payment_id = models.CharField(max_length=100, blank=True, null=True)  # شناسه پرداخت از درگاه
    payment_date = models.DateTimeField(null=True, blank=True)  # زمان پرداخت موفق
    payment_reference_id = models.CharField(max_length=100, blank=True, null=True)  # کد پیگیری پرداخت
    payment_status = models.CharField(max_length=20, default='در انتظار پرداخت', blank=True , verbose_name='payment_status',choices=[
        ('پرداخت شده', 'پرداخت شده'),
        ('در انتظار پرداخت', 'در انتظار پرداخت'),
        ('در انتظار تایید', 'در انتظار تایید'),
        ('ناموفق', 'ناموفق'),
        ('لغو شده', 'لغو شده'),
    ])  # وضعیت پرداخت
    payment_error = models.TextField(blank=True, null=True)  # پیام خطای پرداخت
    
    status = models.CharField(max_length=20, choices=Cart.STATUS_CHOICES, default='در حال انتظار')
    shipping_method = models.CharField(max_length=20, choices=SHIPPING_CHOICES, default='post')
    shipping_cost = models.PositiveIntegerField(default=0)
    total_price = models.PositiveIntegerField()
    discount_code = models.CharField(max_length=50, blank=True, null=True)
    discount_amount = models.PositiveIntegerField(default=0)
    
    shipping_date = models.DateTimeField(null=True, blank=True)
    delivery_date = models.DateField(null=True, blank=True)  # تاریخ تحویل انتخاب شده توسط کاربر
    jalali_delivery_date = models.CharField(max_length=50, blank=True, null=True)  # تاریخ تحویل شمسی
    
    notes = models.TextField(blank=True, null=True)
    
    # Add field tracker to track changes
    tracker = FieldTracker(fields=['status'])
    
    def __str__(self):
        return f"Order #{self.order_number} - {self.user.username}"
    
    def calculate_total(self):
        return self.cart.total_price() + self.shipping_cost - self.discount_amount
        
    def get_shipping_method_display_name(self):
        """نمایش نام فارسی روش ارسال"""
        shipping_methods = dict(self.SHIPPING_CHOICES)
        return shipping_methods.get(self.shipping_method, 'نامشخص')    


@receiver(post_save, sender=Cart)
def create_order_on_payment(sender, instance, created, **kwargs):
    if instance.is_paid and not hasattr(instance, 'order'):
        # اگر سبد پرداخت شده و هنوز سفارشی برای آن ساخته نشده
        from .views import process_payment  # برای استفاده از تابع process_payment
        try:
            # ایجاد سفارش جدید
            order = Order.objects.create(
                user=instance.user,
                cart=instance,
                address=instance.user.clientaddress_set.first(),  # اولین آدرس کاربر
                payment_method='online',
                payment_status='پرداخت شده',
                status='در حال پردازش',
                total_price=instance.total_price()
            )
            print(f"Order created for paid cart: {order.id}")
        except Exception as e:
            print(f"Error creating order: {e}")    