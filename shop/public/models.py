from django.db import models
from colorfield.fields import ColorField
from PIL import Image
from shop.utils.image_uploders import upload_brand_image_path , upload_color_image_path
from shop.categories.models import Category #dont remove this line 
import os

# Create your models here.

# مدل برند  public
class Brand(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="نام ---فارسی")
    en_name = models.CharField(max_length=50, unique=True, verbose_name="نام ---انگلیسی")
    logo = models.ImageField(upload_to=upload_brand_image_path, verbose_name="لوگو برند", blank=True, null=True)
    category = models.ManyToManyField('categories.Category', blank=True, verbose_name="دسته بندی", related_name='Brand')

    class Meta:
        verbose_name = "برند"
        verbose_name_plural = "برندها"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.logo and hasattr(self.logo, 'path') and os.path.isfile(self.logo.path):
            img = Image.open(self.logo.path)
            output_size = (300,300)
            img.thumbnail(output_size, Image.LANCZOS)
            img.save(self.logo.path)

    def __str__(self):
        return self.en_name

# ادامه مدل‌ها public
class BaseColor(models.Model):
    COLOR_PALETTE = [
        ("#FFFFFF", "white"),
        ("#000000", "black"),
        ("#FF0000", "red"),
        ("#008000", "green"),
        ("#0000FF", "blue"),
    ]
    name = models.CharField(max_length=50, verbose_name="نام رنگ", null=True, blank=True)
    color = ColorField(samples=COLOR_PALETTE, default="#FFFFFF", verbose_name="رنگ")
    
    class Meta:
        verbose_name = "رنگ پایه"
        verbose_name_plural = "رنگ های پایه"
        
    def __str__(self):
        return f"{self.name}" if self.name else "بدون نام"
   
# مدل رنگ  public
class Color(models.Model):
    name = models.CharField(max_length=50, verbose_name= "نام رنگ")
    hex_code = models.CharField(max_length=7, verbose_name= "کد هگز رنگ",help_text=" مثال: #FFFFFF")
    image = models.ImageField(upload_to=upload_color_image_path, verbose_name="تصویر رنگ", blank=True, null=True)
    base_color = models.ForeignKey('public.BaseColor', on_delete=models.CASCADE, verbose_name="رنگ پایه", related_name="colors", null=True, blank=True)

    class Meta:
        verbose_name = "رنگ"
        verbose_name_plural = "رنگ ها"
    
    def __str__(self):
        return self.name

# مدل سایز  public
class Size(models.Model):
    SIZE_CHOICES= [
        ("XS","XS"),
        ("S","S"),
        ("M","M"),
        ("L","L"),
        ("XL","XL"),
        ("XXL","XXL"),
        ("3XL","3XL"),
        ("4XL","4XL"),
    ]
    # دسته بندی برای سایزها
    CATEGORY_CHOICES=[
        ("clothing","لباس"),
        ("shoes","کفش"),
        ("accessories","اکسسوری"),
    ]
    size= models.CharField(choices=SIZE_CHOICES, max_length=10, blank= True, null=True, verbose_name="سایز")
    number_size = models.PositiveSmallIntegerField(blank=True, null=True, verbose_name="سایز عددی (برای مواردی مثل کفش)")
    size_numrical = models.CharField(max_length=10, verbose_name="سایز عددی نوشتاری")
    category = models.CharField(choices=CATEGORY_CHOICES, max_length=20, blank=True, null=True, verbose_name="دسته بندی")
    
    class Meta:
        verbose_name = "سایز"
        verbose_name_plural = "سایزها"
        ordering = ['number_size']  # چیدمان پیش‌فرض
        
    def __str__(self):
        if self.size:
            return self.size
        elif self.number_size:
            return str(self.number_size)
        else:
            return self.size_numrical or "بدون سایز"
