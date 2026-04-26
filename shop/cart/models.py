from django.db import models
from shop.products.models import  ProductPackage  # فرض بر این است که این مدل‌ها در shopApp موجود هستند
from account.models import ClientAddress
from django.contrib.auth.models import User
import uuid
from model_utils import FieldTracker  # Add this import
from django.db.models.signals import post_save
from django.dispatch import receiver

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_paid = models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    STATUS_CHOICES = [
            ('در حال انتظار', 'pending'),
            ('تأیید شده', 'confirmed'),
            ('ارسال شده', 'shipped'),
            ('تحویل داده شده', 'delivered'),
            ('لغو شده', 'canceled'),
        ]

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='در حال انتظار')
    cart_number = models.CharField(max_length=100, unique=True, editable=False, default=uuid.uuid4)

    def save(self, *args, **kwargs):
        if not self.cart_number:
            self.cart_number = str(uuid.uuid4())

        # وقتی پرداخت شد، تمام آیتم‌ها قیمتشان را فیکس کنند
        if self.is_paid:
            for item in self.cartitem_set.all():
                if item.final_price is None:
                    item.final_price = item.package.price
                    item.save()

        super(Cart, self).save(*args, **kwargs)

    def total_price(self):
        """ جمع قیمت تمامی آیتم‌ها از فیلد ذخیره‌شده `final_price` """
        return sum(item.total_price() for item in self.cartitem_set.all())

    def calculate_total(self):
        """Alias for total_price to maintain compatibility"""
        return self.total_price()

    def total_goods_price(self):
        """Total price of goods without any discounts"""
        return sum(item.package.price * item.count for item in self.cartitem_set.all())

    def total_discount(self):
        """Total discount amount for all items"""
        total_without_discount = self.total_goods_price()
        final_price = self.total_price()
        return total_without_discount - final_price

    @property
    def total_final_price(self):
        """محاسبه قیمت نهایی کل سبد خرید"""
        return self.total_price()

    def __str__(self):
        return f'Cart of {self.user.username} - Status: {self.get_status_display()}'

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    package = models.ForeignKey(ProductPackage, on_delete=models.CASCADE)
    count = models.PositiveIntegerField(default=1)
    final_price = models.PositiveIntegerField(null=True, blank=True)

    def save(self, *args, **kwargs):
        # اگر سبد پرداخت شده و قیمت نهایی هنوز ثبت نشده، قیمت جاری رو ذخیره کن
        if self.cart.is_paid and self.final_price is None:
            self.final_price = self.package.price
        super().save(*args, **kwargs)

    def get_price(self):
        """گرفتن قیمت: اگر پرداخت شده از final_price، وگرنه از قیمت جاری پکیج"""
        return self.final_price if self.final_price is not None else self.package.price

    def total_price(self):
        """قیمت کل بدون در نظر گرفتن ویژگی جدید"""
        return self.get_price() * self.count

    @property
    def total_final_price(self):
        """محاسبه قیمت نهایی ضربدر تعداد با به‌روزرسانی خودکار"""
        return self.get_price() * self.count

    def __str__(self):
        return f'{self.package.product.name} - {self.count} عدد'

class Order(models.Model):
    SHIPPING_CHOICES = [
        ('post', 'پست'),
        ('tipax', 'تیپاکس'),
        ('express', 'پیک موتوری'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    cart = models.OneToOneField(Cart, on_delete=models.PROTECT)
    address = models.ForeignKey(ClientAddress, on_delete=models.PROTECT)
    
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
    payment_status = models.CharField(max_length=20, default='در انتظار پرداخت', blank=True , verbose_name='وضعیت پرداخت',choices=[
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