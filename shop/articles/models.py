from django.db import models
from django.utils.text import slugify

# Create your models here.


class Article(models.Model):
    title = models.CharField(max_length=200, verbose_name="عنوان مقاله")
    slug = models.SlugField(max_length=250, unique=True, allow_unicode=True, verbose_name="نامک")
    content = models.TextField(verbose_name="محتوای مقاله")
    short_description = models.TextField(max_length=300, blank=True, null=True, verbose_name="توضیح کوتاه")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاریخ به‌روزرسانی")
    image = models.ImageField(upload_to="articles/", null=True, blank=True, verbose_name="تصویر مقاله")
    is_published = models.BooleanField(default=True, verbose_name="منتشر شده")
    
    # SEO Fields
    meta_title = models.CharField(max_length=200, blank=True, null=True, verbose_name="عنوان متا")
    meta_description = models.TextField(blank=True, null=True, verbose_name="توضیحات متا")
    meta_keywords = models.CharField(max_length=300, blank=True, null=True, verbose_name="کلمات کلیدی متا")
    
    class Meta:
        ordering = ["-created_at"]
        verbose_name = "مقاله"
        verbose_name_plural = "مقالات"

    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title, allow_unicode=True)
        super().save(*args, **kwargs)
