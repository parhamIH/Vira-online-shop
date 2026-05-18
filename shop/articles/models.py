from django.db import models
from django.utils.text import slugify

# Create your models here.

#__________________________________________ ------Article------ _______________________________________
class Article(models.Model):
    title = models.CharField(max_length=200, verbose_name=" title")
    slug = models.SlugField(max_length=250, unique=True, allow_unicode=True, verbose_name=" slug")
    content = models.TextField(verbose_name="content")
    short_description = models.TextField(max_length=300, blank=True, null=True, verbose_name=" short_description ")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="created_at")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="updated_at")
    image = models.ImageField(upload_to="articles/", null=True, blank=True, verbose_name="article image")
    is_published = models.BooleanField(default=True, verbose_name="PUBLISHED")
    
    # SEO Fields
    meta_title = models.CharField(max_length=200, blank=True, null=True, verbose_name="meta title ")
    meta_description = models.TextField(blank=True, null=True, verbose_name=" meta description")
    meta_keywords = models.CharField(max_length=300, blank=True, null=True, verbose_name="meta  keywords")
    
    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Article"
        verbose_name_plural = "Articles"

    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title, allow_unicode=True)
        super().save(*args, **kwargs)
