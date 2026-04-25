from django.db import models
from PIL import Image  # pillow
from mptt.models import MPTTModel, TreeForeignKey
from shop.public.models import Brand
import os 
# Create your models here.


class BaseCategorys(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="اسم  --  فارسی --  دسته بندی اصلی")
    en_name = models.CharField(max_length=50, unique=True, verbose_name="اسم- --انگلیسی-- دسته بندی اصلی")
    description = models.TextField(verbose_name="توضیحات دسته بندی اصلی")
    image = models.ImageField(upload_to=upload_BaseCategory_image_path, verbose_name="عکس دسته بندی اصلی", blank=True, null=True)
    brands = models.ManyToManyField('Brand', verbose_name="برند های دسته بندی", related_name='base_categories', blank=True)

    class Meta:
        verbose_name = "دسته بندی  اصلی "
        verbose_name_plural = "دسته بندی های اصلی"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.image and hasattr(self.image, 'path') and os.path.isfile(self.image.path):
            img = Image.open(self.image.path)
            output_size = (300,300)
            img.thumbnail(output_size, Image.LANCZOS)
            img.save(self.image.path)

    def __str__(self):
        return self.name

class Category(MPTTModel):

    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    base_catgory = models.ForeignKey(BaseCategorys, verbose_name="دسته بندی اصلی", on_delete=models.CASCADE, related_name='categories')

    name = models.CharField(max_length=100,unique=True, verbose_name='نام دسته‌بندی')
    en_name = models.CharField(max_length=20, unique=True, verbose_name="نام دسته بندی ---انگلیسی")
    description = models.TextField(blank=True, null=True)
    brand = models.ManyToManyField(Brand, blank=True, related_name='categories')
    image = models.ImageField(upload_to=upload_cat_image_path, verbose_name="عکس دسته بندی", blank=True, null=True)

    class MPTTMeta:
        order_insertion_by = ["parent", "name"]

    class Meta:
        verbose_name = 'دسته‌بندی'
        verbose_name_plural = 'دسته‌بندی‌ها'



    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.image and hasattr(self.image, 'path') and os.path.isfile(self.image.path):
            img = Image.open(self.image.path)
            output_size = (300,300)
            img.thumbnail(output_size, Image.LANCZOS)
            img.save(self.image.path)


    def __str__(self):
        return self.name
