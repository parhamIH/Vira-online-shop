from django.db import models
from colorfield.fields import ColorField
from PIL import Image
from shop.utils.image_uploders import upload_brand_image_path , upload_color_image_path
from shop.categories.models import Category #dont remove this line 
import os

# Create your models here.

# مدل برند  public
class Brand(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="name---fasri")
    en_name = models.CharField(max_length=50, unique=True, verbose_name="name---english")
    logo = models.ImageField(upload_to=upload_brand_image_path, verbose_name="Brand logo", blank=True, null=True)
    category = models.ManyToManyField(Category, blank=True, verbose_name="Brand caregory")

    class Meta:
        verbose_name = "Brand"
        verbose_name_plural = "Brands"

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
    name = models.CharField(max_length=50, verbose_name="base color name ", null=True, blank=True)
    color = ColorField(samples=COLOR_PALETTE, default="#FFFFFF", verbose_name="color value <-->(hex)")
    
    class Meta:
        verbose_name = "Base Color"
        verbose_name_plural = "Base Colors"
        
    def __str__(self):
        return f"{self.name}" if self.name else "name less"
   
# مدل رنگ  public
class Color(models.Model):
    name = models.CharField(max_length=50, verbose_name="colr name")
    hex_code = models.CharField(max_length=7, verbose_name="color value <-->(hex)" ,help_text=" مثال: #FFFFFF")
    image = models.ImageField(upload_to=upload_color_image_path, verbose_name="image for color ", blank=True, null=True)
    base_color = models.ForeignKey('public.BaseColor', on_delete=models.CASCADE, verbose_name="base color  ", related_name="colors", null=True, blank=True)

    class Meta:
        verbose_name = "color"
        verbose_name_plural = "colors"
    
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
    size= models.CharField(choices=SIZE_CHOICES, max_length=10, blank= True, null=True, verbose_name="ware size ")
    number_size = models.PositiveSmallIntegerField(blank=True, null=True, verbose_name="Numrical size " help_text="for shoes or etc... (*postive int*) ")
    size_numrical = models.CharField(max_length=10, verbose_name="Numrical size " help_text="write able")
    category = models.CharField(choices=CATEGORY_CHOICES, max_length=20, blank=True, null=True, verbose_name="category")
    
    class Meta:
        verbose_name = "size"
        verbose_name_plural = "sizes "
        ordering = ['number_size']  # چیدمان پیش‌فرض
        
    def __str__(self):
        if self.size:
            return self.size
        elif self.number_size:
            return str(self.number_size)
        else:
            return self.size_numrical or "size less "
