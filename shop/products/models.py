from django.db import models
from PIL import Image
from shop.public.models import Warranty, Size, Color
from shop.providers.models import Provider
from django.core.validators import MinValueValidator, MaxValueValidator
from model_utils import FieldTracker  # Add this import
from shop.utils.image_uploders import upload_image_path
import os 
# Create your models here.

#__________________________________________ ------Product------ _______________________________________
class Product(models.Model):
    name = models.CharField(max_length=150, unique= True, verbose_name="name")
    description = models.TextField(verbose_name="description")
    is_active = models.BooleanField(default=False, verbose_name="active")
    categories = models.ManyToManyField('categories.Category', verbose_name="categories")
    
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE, related_name='product', null=True, blank=True)

    created_date = models.DateTimeField(auto_now_add=True, verbose_name="created_date")
    updated_date = models.DateTimeField(auto_now=True, verbose_name="last update")
    image = models.ImageField(upload_to='uploads/', verbose_name="image", blank=True, null=True)  # مسیر بارگذاری تصویر را تنظیم کنید

    class Meta:
        verbose_name = "product"
        verbose_name_plural = "products"
        permissions = [
            ("manage_own_products", "Can manage own products"),
        ]
    def __str__(self):
        return f"نام محصول: {self.name}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # باز کردن تصویر
        if self.image and hasattr(self.image, 'path') and os.path.isfile(self.image.path):
            img = Image.open(self.image.path)
            # تنظیم ابعاد جدید
            output_size = (800, 800)
            # تغییر اندازه تصویر به ابعاد مشخص
            img = img.resize(output_size, Image.LANCZOS)  # استفاده از LANCZOS برای کیفیت بهتر
            # ذخیره تصویر با ابعاد جدید
            img.save(self.image.path)

#__________________________________________ ------ProductPackage------ _______________________________________
class ProductPackage(models.Model):
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE, related_name='product_packages',  null=True)
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE, related_name='product_packageser', null=True, blank=True)
    waranty = models.ForeignKey( Warranty , on_delete=models.CASCADE, related_name='product_packages')

    # ____________________________________________________*product attributes *___________________________________________
    size = models.ForeignKey('public.Size', on_delete=models.CASCADE, default=None, blank=True, null=True)
    brand = models.ForeignKey('public.Brand', on_delete=models.CASCADE, default=None, blank=True, null=True, verbose_name="brand")
    color = models.ForeignKey('public.Color',verbose_name="color", blank= True,null=True, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0, verbose_name="quantity" , blank= False)
    weight = models.PositiveIntegerField(verbose_name="weight to geram" , default= 0 , blank= True,null=True)
    is_active_package=models.BooleanField(default=False, verbose_name="is active" )
    created_date = models.DateTimeField(auto_now_add=True)
    attributs = models.JSONField (default=dict, blank=True, null=True)
    
    # _________________________________________________*price*_____________________________________________________
    price = models.BigIntegerField(null=False, verbose_name="base price")
    final_price = models.BigIntegerField(default= 0 , verbose_name= "final price ",editable=False)
    discount = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(99)], null=True, blank=True ,default=0, verbose_name="discount percentage")
    is_active_discount = models.BooleanField(default=False, verbose_name="active discount ")
    
    # آمار فروش
    sold_count = models.PositiveIntegerField(default=0, verbose_name="sold_count")
    views_count = models.PositiveIntegerField(default=0, verbose_name="views_count")
    rating = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(5)], verbose_name="rate")

    # Add field tracker to track changes
    tracker = FieldTracker(fields=['is_active_package'])

    class Meta:
        verbose_name = "product package  "
        verbose_name_plural = " product packages"

        permissions = [
            ("manage_own_packages", "Can manage own packages"),
        ]

    def __str__(self):
        size_str = self.size.size if self.size else "size less "
        return f"{self.product.id} - {self.product.name} - {size_str} - {self.quantity} - {self.weight} - "
    
    @property
    def discounted_price(self):
        return (self.price * self.discount) / 100
    
    def save(self, *args, **kwargs):
        # محاسبه قیمت نهایی با توجه به تخفیف
        if self.is_active_discount and self.discount > 0:
            self.final_price = self.price - int((self.price * self.discount) / 100)
        else:
            self.final_price = self.price
            
        super().save(*args, **kwargs)


#__________________________________________ ------Gallery------ _______________________________________
class Gallery(models.Model):

    product = models.ForeignKey('products.Product',on_delete=models.CASCADE,verbose_name="product")

    image = models.ImageField(upload_to=upload_image_path,verbose_name="image", blank=True, null=True)

    class Meta :
        verbose_name ="image"
        verbose_name_plural = "gallery"
    
    def __str__(self):
        return f"{self.product}"
        
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.image and hasattr(self.image, 'path') and os.path.isfile(self.image.path):
            img = Image.open(self.image.path)
            output_size = (800, 800)
            img = img.resize(output_size, Image.LANCZOS)
            img.save(self.image.path)

