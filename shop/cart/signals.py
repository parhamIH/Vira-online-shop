from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import CartItem

@receiver(pre_save, sender=CartItem)
def update_cart_item_count(sender, instance, **kwargs):
    # بررسی وجود CartItem با همان محصول و سبد خرید
    existing_item = CartItem.objects.filter(product=instance.product, cart=instance.cart).first()
    
    if existing_item:
        # اگر آیتم موجود باشد، count آن را افزایش می‌دهیم
        existing_item.count += instance.count  # افزایش count با مقدار جدید
        existing_item.save()  # ذخیره تغییرات
        # جلوگیری از ذخیره شیء جدید
        instance.pk = existing_item.pk  # تعیین primary key برای جلوگیری از ایجاد رکورد جدید
