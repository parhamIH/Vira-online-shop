from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from cart.models import Cart, Order
from account.models import Notification, Favourite_products
from shopApp.models import ProductPackage, Comment
from model_utils import FieldTracker

# ایجاد اعلان برای تغییر وضعیت سفارش
@receiver(post_save, sender=Order)
def order_status_notification(sender, instance, created, **kwargs):
    if not hasattr(instance, 'tracker'):
        return
        
    if not created:  # فقط برای بروزرسانی‌های سفارش
        # بررسی تغییر وضعیت سفارش
        if instance.tracker.has_changed('status'):
            old_status = instance.tracker.previous('status')
            new_status = instance.status
            
            # ایجاد پیام مناسب بر اساس وضعیت جدید
            status_messages = {
                'تأیید شده': {
                    'title': 'سفارش شما تأیید شد',
                    'message': f'سفارش شما با شماره {instance.order_number} تأیید شده و در حال آماده‌سازی است.',
                    'type': 'success'
                },
                'ارسال شده': {
                    'title': 'سفارش شما ارسال شد',
                    'message': f'سفارش شما با شماره {instance.order_number} ارسال شده و بزودی به دست شما می‌رسد.',
                    'type': 'info'
                },
                'تحویل داده شده': {
                    'title': 'سفارش شما تحویل داده شد',
                    'message': f'سفارش شما با شماره {instance.order_number} تحویل داده شده است. از خرید شما سپاسگزاریم.',
                    'type': 'success'
                },
                'لغو شده': {
                    'title': 'سفارش شما لغو شد',
                    'message': f'متاسفانه سفارش شما با شماره {instance.order_number} لغو شده است. برای اطلاعات بیشتر با پشتیبانی تماس بگیرید.',
                    'type': 'danger'
                }
            }
            
            if new_status in status_messages:
                msg = status_messages[new_status]
                Notification.objects.create(
                    user=instance.user,
                    title=msg['title'],
                    message=msg['message'],
                    notification_type=msg['type'],
                    related_url=f'/profile/orders/{instance.id}/'
                )

# اعلان برای زمانی که محصول موجود می‌شود (از علاقه‌مندی‌ها)
@receiver(post_save, sender=ProductPackage)
def product_availability_notification(sender, instance, created, **kwargs):
    if not hasattr(instance, 'tracker'):
        return
        
    if not created and instance.is_active_package:
        # اگر محصول فعال شده و قبلاً غیرفعال بوده
        if instance.tracker.has_changed('is_active_package') and not instance.tracker.previous('is_active_package'):
            # پیدا کردن کاربرانی که این محصول را به علاقه‌مندی‌ها اضافه کرده‌اند
            favorite_users = Favourite_products.objects.filter(products=instance.product)
            
            for fav in favorite_users:
                Notification.objects.create(
                    user=fav.user,
                    title='محصول مورد علاقه شما موجود شد',
                    message=f'محصول {instance.product.name} که در لیست علاقه‌مندی‌های شما قرار دارد، اکنون موجود است.',
                    notification_type='success',
                    related_url=f'/product/{instance.product.id}/{instance.product.name}'
                )

# اعلان برای نظرات جدید یا پاسخ به نظرات
@receiver(post_save, sender=Comment)  # فرض شده که مدل Comment وجود دارد
def comment_notification(sender, instance, created, **kwargs):
    if created and hasattr(instance, 'parent') and instance.parent:
        Notification.objects.create(
            user=instance.parent.user,
            title='پاسخ به نظر شما',
            message=f'پاسخی به نظر شما درباره محصول "{instance.product.name}" داده شده است.',
            notification_type='info',
            related_url=f'/product/{instance.product.id}/{instance.product.name}#comment-{instance.id}'
        )