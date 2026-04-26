from django.db import models
from PIL import Image
from shop.public.models import Brand
from shop.utils.image_uploders import upload_slider_image_path , upload_banner_image_path
import os

# Create your models here.

class HomeSlider(models.Model):
    title = models.CharField(max_length=100, blank=True, null=True, verbose_name="عنوان اسلاید")
    subtitle = models.CharField(max_length=200, blank=True, null=True, verbose_name="زیرعنوان اسلاید")
    image = models.ImageField(upload_to=upload_slider_image_path, verbose_name="تصویر اسلاید", blank=True, null=True)
    link = models.URLField(verbose_name="لینک", blank=True, null=True)
    active = models.BooleanField(default=True, verbose_name="فعال")
    order = models.PositiveIntegerField(default=0, verbose_name="ترتیب نمایش")
    
    class Meta:
        verbose_name = "اسلایدر صفحه اصلی"
        verbose_name_plural = "اسلایدرهای صفحه اصلی"
        ordering = ['order']
        
    def __str__(self):
        return self.title or f"اسلاید {self.id}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.image and hasattr(self.image, 'path') and os.path.isfile(self.image.path):
            img = Image.open(self.image.path)
            output_size = (1920, 800)  # مناسب برای اسلایدر عریض
            img = img.resize(output_size, Image.LANCZOS)
            img.save(self.image.path)


class PromotionalBanner(models.Model):
    POSITION_CHOICES = [
        ('top', 'بالای صفحه'),
        ('middle', 'وسط صفحه'),
        ('bottom', 'پایین صفحه'),
    ]
    
    SIZE_CHOICES = [
        ('full', 'تمام عرض'),
        ('half', 'نیم عرض'),
        ('third', 'یک سوم'),
    ]
    
    title = models.CharField(max_length=100, blank=True, null=True, verbose_name="عنوان بنر")
    image = models.ImageField(upload_to=upload_banner_image_path, verbose_name="تصویر بنر", blank=True, null=True)
    link = models.URLField(verbose_name="لینک", blank=True, null=True)
    position = models.CharField(max_length=10, choices=POSITION_CHOICES, default='middle', verbose_name="موقعیت در صفحه")
    size = models.CharField(max_length=10, choices=SIZE_CHOICES, default='full', verbose_name="اندازه بنر")
    active = models.BooleanField(default=True, verbose_name="فعال")
    order = models.PositiveIntegerField(default=0, verbose_name="ترتیب نمایش")
    
    class Meta:
        verbose_name = "بنر تبلیغاتی"
        verbose_name_plural = "بنرهای تبلیغاتی"
        ordering = ['position', 'order']
        
    def __str__(self):
        return self.title or f"بنر {self.id}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.image and hasattr(self.image, 'path') and os.path.isfile(self.image.path):
            img = Image.open(self.image.path)
            # تنظیم اندازه بر اساس نوع بنر
            if self.size == 'full':
                output_size = (1200, 300)
            elif self.size == 'half':
                output_size = (600, 300)
            else:  # third
                output_size = (400, 300)
            img = img.resize(output_size, Image.LANCZOS)
            img.save(self.image.path)

# مدل برای نمایش ویژه برندها در صفحه اصلی
class FeaturedBrand(models.Model):
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, verbose_name="برند")
    active = models.BooleanField(default=True, verbose_name="فعال")
    order = models.PositiveIntegerField(default=0, verbose_name="ترتیب نمایش")
    
    class Meta:
        verbose_name = "برند ویژه"
        verbose_name_plural = "برندهای ویژه"
        ordering = ['order']
        
    def __str__(self):
        return f"{self.brand.name}"

