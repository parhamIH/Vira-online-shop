from django.db import models
from PIL import Image
# Create your models here.



# مدل تنظیمات کلی سایت
class SiteSettings(models.Model):
    site_name = models.CharField(max_length=100, verbose_name="نام سایت")
    site_url = models.URLField(verbose_name="آدرس سایت")
    logo = models.ImageField(upload_to='settings/', verbose_name="لوگوی سایت", blank=True, null=True)
    favicon = models.ImageField(upload_to='settings/', verbose_name="فاوآیکون سایت", blank=True, null=True)
    
    # اطلاعات تماس
    email = models.EmailField(verbose_name="ایمیل")
    phone = models.CharField(max_length=20, verbose_name="شماره تماس")
    address = models.TextField(verbose_name="آدرس")
    
    # شبکه‌های اجتماعی
    instagram = models.URLField(blank=True, null=True, verbose_name="اینستاگرام")
    telegram = models.URLField(blank=True, null=True, verbose_name="تلگرام")
    twitter = models.URLField(blank=True, null=True, verbose_name="توییتر")
    linkedin = models.URLField(blank=True, null=True, verbose_name="لینکدین")
    
    # متن‌های سایت
    footer_text = models.TextField(verbose_name="متن فوتر")
    about_text = models.TextField(verbose_name="درباره ما")
    
    # تنظیمات سئو
    seo_keywords = models.TextField(verbose_name="کلمات کلیدی سئو", blank=True, null=True)
    seo_description = models.TextField(verbose_name="توضیحات سئو", blank=True, null=True)
    
    # تنظیمات فروشگاه
    shipping_cost = models.PositiveIntegerField(default=0, verbose_name="هزینه ارسال")
    free_shipping_threshold = models.PositiveIntegerField(default=0, verbose_name="حداقل خرید برای ارسال رایگان")
    tax_percentage = models.FloatField(default=9.0, verbose_name="درصد مالیات")
    
    class Meta:
        verbose_name = "تنظیمات سایت"
        verbose_name_plural = "تنظیمات سایت"
        
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

# مدل صفحات استاتیک (مانند قوانین و مقررات، درباره ما)
class StaticPage(models.Model):
    title = models.CharField(max_length=200, verbose_name="عنوان صفحه")
    slug = models.SlugField(unique=True, verbose_name="نامک")
    content = models.TextField(verbose_name="محتوای صفحه")
    active = models.BooleanField(default=True, verbose_name="فعال")
    
    # تنظیمات سئو
    seo_title = models.CharField(max_length=200, blank=True, null=True, verbose_name="عنوان سئو")
    seo_keywords = models.TextField(blank=True, null=True, verbose_name="کلمات کلیدی سئو")
    seo_description = models.TextField(blank=True, null=True, verbose_name="توضیحات سئو")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاریخ بروزرسانی")
    
    class Meta:
        verbose_name = "صفحه استاتیک"
        verbose_name_plural = "صفحات استاتیک"
        
    def __str__(self):
        return self.title

