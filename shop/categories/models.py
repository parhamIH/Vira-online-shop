from django.db import models
from PIL import Image  # pillow
from shop.utils.image_uploders import upload_BaseCategory_image_path , upload_cat_image_path
import os 

# Create your models here.

#__________________________________________ ------BaseCategories------ _______________________________________
class BaseCategories(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="base category name --- farsi")
    en_name = models.CharField(max_length=50, unique=True, verbose_name="base category name --- english")
    description = models.TextField(verbose_name="description")
    image = models.ImageField(upload_to=upload_BaseCategory_image_path, verbose_name="base category image", blank=True, null=True)
    brands = models.ManyToManyField('public.Brand', verbose_name="base category Brands", related_name='base_categories', blank=True)

    class Meta:
        verbose_name = "Base Category"
        verbose_name_plural = "Base Categories"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.image and hasattr(self.image, 'path') and os.path.isfile(self.image.path):
            img = Image.open(self.image.path)
            output_size = (300,300)
            img.thumbnail(output_size, Image.LANCZOS)
            img.save(self.image.path)

    def __str__(self):
        return self.name

#__________________________________________ ------Category------ _______________________________________
class Category(models.Model):
    parent = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True, verbose_name=" parent category ", related_name='subcategories')
    base_catgory = models.ForeignKey(BaseCategories, verbose_name="main category", on_delete=models.CASCADE, related_name='categories')
    name = models.CharField(max_length=20, unique=True, verbose_name="category name ---farsi")
    en_name = models.CharField(max_length=20, unique=True, verbose_name="category name ---english")
    description = models.TextField(verbose_name="description ")
    image = models.ImageField(upload_to=upload_cat_image_path, verbose_name="category image", blank=True, null=True)

    class Meta:
        verbose_name = "category"
        verbose_name_plural = "categories"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.image and hasattr(self.image, 'path') and os.path.isfile(self.image.path):
            img = Image.open(self.image.path)
            output_size = (300,300)
            img.thumbnail(output_size, Image.LANCZOS)
            img.save(self.image.path)

    def __str__(self):
        return self.name

