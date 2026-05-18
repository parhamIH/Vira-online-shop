from django.db import models
from PIL import Image
import os
# Create your models here.


#__________________________________________ ------SiteSettings------ _______________________________________
# مدل تنظیمات کلی سایت
class SiteSettings(models.Model):
    site_name = models.CharField(max_length=100, verbose_name="site name")
    site_url = models.URLField(verbose_name="site url")
    logo = models.ImageField(upload_to='settings/', verbose_name="site logo", blank=True, null=True)
    favicon = models.ImageField(upload_to='settings/', verbose_name="favicon", help_text="needed to hard refresh <--> (shift + f5)", blank=True, null=True)
    
    # اطلاعات تماس
    email = models.EmailField(verbose_name="Owner email")
    phone = models.CharField(max_length=20, verbose_name="Owner phone")
    address = models.TextField(verbose_name="Owner address")
    
    # شبکه‌های اجتماعی
    instagram = models.URLField(blank=True, null=True, verbose_name="instagram")
    telegram = models.URLField(blank=True, null=True, verbose_name="telegram")
    twitter= models.URLField(blank=True, null=True, verbose_name="twitter")
    linkedin = models.URLField(blank=True, null=True, verbose_name="linkedin")
    
    # متن‌های سایت
    footer_text = models.TextField(verbose_name="footer text ")
    about_text = models.TextField(verbose_name="about_text")
    
    # تنظیمات سئو
    seo_keywords = models.TextField(verbose_name="seo_keywords", blank=True, null=True)
    seo_description = models.TextField(verbose_name="seo_description", blank=True, null=True)
    
    # تنظیمات فروشگاه
    shipping_cost = models.PositiveIntegerField(default=0, verbose_name="shipping_cost")
    free_shipping_threshold = models.PositiveIntegerField(default=0, verbose_name="free_shipping_threshold")
    tax_percentage = models.FloatField(default=9.0, verbose_name="tax_percentage")
    
    class Meta:
        verbose_name = "site setting"
        verbose_name_plural = "site settings"
        
    def __str__(self):
        return self.site_name

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.logo and hasattr(self.logo, 'path') and os.path.isfile(self.logo.path):
            img = Image.open(self.logo.path)
            output_size = (300, 100)
            img.thumbnail(output_size, Image.LANCZOS)
            img.save(self.logo.path)
            
        if self.favicon and hasattr(self.favicon, 'path') and os.path.isfile(self.favicon.path):
            img = Image.open(self.favicon.path)
            output_size = (32, 32)
            img = img.resize(output_size, Image.LANCZOS)
            img.save(self.favicon.path)
            
#__________________________________________ ------StaticPage------ _______________________________________
# مدل صفحات استاتیک (مانند قوانین و مقررات، درباره ما)
class StaticPage(models.Model):
    title = models.CharField(max_length=200, verbose_name="page title ")
    slug = models.SlugField(unique=True, verbose_name="page slug")
    content = models.TextField(verbose_name="page content")
    active = models.BooleanField(default=True, verbose_name="active")
    
    # تنظیمات سئو
    seo_title = models.CharField(max_length=200, blank=True, null=True, verbose_name="seo_title")
    seo_keywords = models.TextField(blank=True, null=True, verbose_name="seo_keywords")
    seo_description = models.TextField(blank=True, null=True, verbose_name="seo_description")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="created_at")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="updated_at")
    
    class Meta:
        verbose_name = "static page  "
        verbose_name_plural = "static pages  "
        
    def __str__(self):
        return self.title

