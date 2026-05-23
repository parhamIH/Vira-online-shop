from django.db import models
from django.core.validators import MinLengthValidator, RegexValidator
from django.contrib.auth.models import User
from shop.products.models import Product
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError

# Custom validator for Iranian national ID
def validate_iranian_national_id(national_id):
    """
    اعتبارسنجی کد ملی ایرانی
    
    شرایط کد ملی معتبر:
    1. دقیقاً 10 رقم باشد
    2. همه کاراکترها عدد باشند
    3. الگوریتم اعتبارسنجی کد ملی را پاس کند
    
    ساختار کد ملی:
    - 9 رقم اول: شماره اصلی
    - رقم دهم: رقم کنترلی
    """
    # بررسی طول کد ملی
    if not national_id or len(national_id) != 10:
        return False
    
    # بررسی عددی بودن تمام کاراکترها
    if not national_id.isdigit():
        return False
    
    # بررسی الگوی کدهای ملی غیرمعتبر مانند 0000000000 و 1111111111
    if national_id in ['0000000000', '1111111111', '2222222222', '3333333333', 
                      '4444444444', '5555555555', '6666666666', '7777777777', 
                      '8888888888', '9999999999']:
        return False
    
    # محاسبه رقم کنترلی
    check = int(national_id[9])
    sum_digits = 0
    
    for i in range(9):
        sum_digits += int(national_id[i]) * (10 - i)
    
    remainder = sum_digits % 11
    
    if remainder < 2:
        return check == remainder
    else:
        return check == 11 - remainder

def validate_national_id(value):
    if not validate_iranian_national_id(value):
        raise ValidationError(
            'کد ملی وارد شده معتبر نیست. کد ملی باید 10 رقم بوده و با الگوریتم صحیح کد ملی جمهوری اسلامی ایران مطابقت داشته باشد.'
        )

# Create your models here.
#__________________________________________ ------Favourite-Products------ _______________________________________

class FavouriteProducts(models.Model):
    user=models.ForeignKey(User, on_delete=models.CASCADE)
    products=models.ManyToManyField(Product, verbose_name=("FavouriteProducts"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Favorites"

#__________________________________________ ------Client-Address------ _______________________________________
class ClientAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title_address= models.CharField(max_length=50)
    province = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    full_address = models.TextField()
    postcode =models.CharField(max_length=10,validators=[MinLengthValidator(10)])

    def __str__(self):
        return f"{self.city}, {self.province} - {self.full_address}"

#__________________________________________ ------Notification------ _______________________________________
class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('info', 'اطلاعات'),
        ('success', 'موفقیت'),
        ('warning', 'هشدار'),
        ('danger', 'خطر'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications', verbose_name="Client")
    title = models.CharField(max_length=255, verbose_name="Notification title")
    message = models.TextField(verbose_name="Notification message")
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='info', verbose_name="Notification Type ")
    is_read = models.BooleanField(default=False, verbose_name="is_read")
    related_url = models.CharField(max_length=255, blank=True, null=True, verbose_name="related_url")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="created_at")
    
    class Meta:
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.user.username}"
        
    def mark_as_read(self):
        self.is_read = True
        self.save()

#__________________________________________ ------Client-Profile------ _______________________________________
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone_number = models.CharField(max_length=15, unique=True, null=True, blank=True, verbose_name="phone_number")
    is_phone_verified = models.BooleanField(default=False, verbose_name="is_phone_verified")
    verification_code = models.CharField(max_length=6, null=True, blank=True, verbose_name="verification_code")
    verification_code_created_at = models.DateTimeField(null=True, blank=True, verbose_name="verification_code_created_at")
    national_id = models.CharField(
        max_length=10, 
        null=True, 
        blank=True, 
        validators=[
            RegexValidator(
                regex=r'^\d{10}$', 
                message='کد ملی باید دقیقاً 10 رقم باشد'
            ),
            validate_national_id
        ],
        verbose_name="national_id"
    )
    birth_date = models.DateField(null=True, blank=True, verbose_name=" birth_date")
    job = models.CharField(max_length=100, null=True, blank=True, verbose_name="job")
    economic_code = models.CharField(max_length=12, null=True, blank=True, verbose_name="economic_code")
    legal_info = models.TextField(null=True, blank=True, verbose_name="legal_info")
    refund_method = models.CharField(max_length=100, null=True, blank=True, verbose_name="refund_method")
    
    class Meta:
        verbose_name = "Profile"
        verbose_name_plural = "Profiles"
    
    def __str__(self):
        return f"{self.user.username} - {self.phone_number}"

# Signal برای ایجاد خودکار Profile هنگام ایجاد User
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
#__________________________________________ ------User-Coupons------ _______________________________________
class UserCoupon(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='offer_coupons')
    code = models.CharField(max_length=50)
    discount = models.PositiveIntegerField(help_text="discount")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expire_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.code}  --- ({self.user.username})"
