from django.db import models
from PIL import Image
from shop.public.models import Brand
from shop.utils.image_uploders import upload_slider_image_path , upload_banner_image_path
import os

# Create your models here.
#__________________________________________ ------HomeSlider------ _______________________________________
class HomeSlider(models.Model):
    title = models.CharField(max_length=100, blank=True, null=True, verbose_name="Slide title")
    subtitle = models.CharField(max_length=200, blank=True, null=True, verbose_name="Slide subtitle  ")
    image = models.ImageField(upload_to=upload_slider_image_path, verbose_name="Slide image ", blank=True, null=True)
    link = models.URLField(verbose_name="link", blank=True, null=True)
    active = models.BooleanField(default=True, verbose_name="active")
    order = models.PositiveIntegerField(default=0, verbose_name="slid order")
    
    class Meta:
        verbose_name = "index page slider"
        verbose_name_plural = "index page sliders"
        ordering = ['order']
        
    def __str__(self):
        return self.title or f"Slide : {self.id}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.image and hasattr(self.image, 'path') and os.path.isfile(self.image.path):
            img = Image.open(self.image.path)
            output_size = (1920, 800)  # مناسب برای اسلایدر عریض
            img = img.resize(output_size, Image.LANCZOS)
            img.save(self.image.path)

#__________________________________________ ------PromotionalBanner------ _______________________________________
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
    
    title = models.CharField(max_length=100, blank=True, null=True, verbose_name="Banner title")
    image = models.ImageField(upload_to=upload_banner_image_path, verbose_name="Banner image", blank=True, null=True)
    link = models.URLField(verbose_name="link", blank=True, null=True)
    position = models.CharField(max_length=10, choices=POSITION_CHOICES, default='middle', verbose_name="Banner position ")
    size = models.CharField(max_length=10, choices=SIZE_CHOICES, default='full', verbose_name="Banner size")
    active = models.BooleanField(default=True, verbose_name="active")
    order = models.PositiveIntegerField(default=0, verbose_name="order")
    
    class Meta:
        verbose_name = "Promotional Banner"
        verbose_name_plural = "Promotional Banners "
        ordering = ['position', 'order']
        
    def __str__(self):
        return self.title or f"Banner {self.id}"
    
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
#__________________________________________ ------FeaturedBrand------ _______________________________________
# مدل برای نمایش ویژه برندها در صفحه اصلی
class FeaturedBrand(models.Model):
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, verbose_name="Brand")
    active = models.BooleanField(default=True, verbose_name="active")
    order = models.PositiveIntegerField(default=0, verbose_name="order")
    
    class Meta:
        verbose_name = " Featured Brand"
        verbose_name_plural = "Featured Brands "
        ordering = ['order']
        
    def __str__(self):
        return f"{self.brand.name}"

