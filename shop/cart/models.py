from django.db import models
from django.contrib.auth.models import User
import uuid
from model_utils import FieldTracker  # Add this import
from django.db.models.signals import post_save
from django.dispatch import receiver

#__________________________________________ ------Cart------ _______________________________________
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
                if item.final_price is None or item.final_price > item.price :
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

#__________________________________________ ------CartItem------ _______________________________________
class CartItem(models.Model):
    cart = models.ForeignKey('cart.Cart', on_delete=models.CASCADE)
    package = models.ForeignKey('products.ProductPackage', on_delete=models.CASCADE)
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
