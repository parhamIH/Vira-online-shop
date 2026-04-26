from django.db import models
from PIL import Image
from shop.public.models import Size , Color
from django.core.validators import MinValueValidator, MaxValueValidator
from model_utils import FieldTracker  # Add this import
from utils.image_uploders import upload_image_path
import os 
# Create your models here.

# مدل محصول product
class Product(models.Model):
    name = models.CharField(max_length=150, unique= True, verbose_name="نام محصول")
    description = models.TextField(verbose_name="توضیحات")
    is_active = models.BooleanField(default=False, verbose_name="موجود")
    categories = models.ManyToManyField('Category', verbose_name="دسته بندی")
    
    created_date = models.DateTimeField(auto_now_add=True, verbose_name="زمان اضافه شدن")
    updated_date = models.DateTimeField(auto_now=True, verbose_name="آخرین تغییر")
    image = models.ImageField(upload_to='uploads/', verbose_name="عکس", blank=True, null=True)  # مسیر بارگذاری تصویر را تنظیم کنید

    class Meta:
        verbose_name = "محصول"
        verbose_name_plural = "محصولات"

    def __str__(self):
        return f"نام محصول: {self.name}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # باز کردن تصویر
        if self.image and hasattr(self.image, 'path') and os.path.isfile(self.image.path):
            img = Image.open(self.image.path)
            # تنظیم ابعاد جدید
            output_size = (800, 800)
            # تغییر اندازه تصویر به ابعاد مشخص
            img = img.resize(output_size, Image.LANCZOS)  # استفاده از LANCZOS برای کیفیت بهتر
            # ذخیره تصویر با ابعاد جدید
            img.save(self.image.path)

# مدل ویژگی های محصول product 
class ProductPackage(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='product_packages')
    # ____________________________________________________*product attributes *___________________________________________
    size = models.ForeignKey(Size, on_delete=models.CASCADE, default=None, blank=True, null=True)
    brand = models.ForeignKey('Brand', on_delete=models.CASCADE, default=None, blank=True, null=True, verbose_name="برند")
    color = models.ForeignKey(Color,verbose_name="رنگ", blank= True,null=True, on_delete=models.CASCADE)

    quantity = models.PositiveIntegerField(default=0, verbose_name="تعداد" , blank= False)
    weight = models.PositiveIntegerField(verbose_name="وزن به گرم" , default= 0 , blank= True,null=True)

    is_active_package=models.BooleanField(default=False ,  verbose_name=" موجود ؟" , )

    created_date = models.DateTimeField(auto_now_add=True)
    
    # _________________________________________________*price*_____________________________________________________
    price = models.BigIntegerField(null=False, verbose_name="قیمت برای این ویژگی ها")
    final_price = models.BigIntegerField(default= 0 , verbose_name= "  قیمت نهایی با این ویژگی ها ",editable=False)
    discount = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(99)], null=True, blank=True ,default=0, verbose_name="درصد تخفیف")
    is_active_discount = models.BooleanField(default=False, verbose_name="اعمال تخفیف")
    
    # آمار فروش
    sold_count = models.PositiveIntegerField(default=0, verbose_name="تعداد فروش")
    views_count = models.PositiveIntegerField(default=0, verbose_name="تعداد بازدید")
    rating = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(5)], verbose_name="امتیاز")

    # Add field tracker to track changes
    tracker = FieldTracker(fields=['is_active_package'])

    class Meta:
        verbose_name = " ویژگی های محصول"
        verbose_name_plural = " ویژگی های محصولات"

    def __str__(self):
        size_str = self.size.size if self.size else "بدون سایز"
        return f"{self.product.id} - {self.product.name} - {size_str} - {self.quantity} - {self.weight} - "


    @property
    def discounted_price(self):
        return (self.price * self.discount) / 100
    
    def save(self, *args, **kwargs):
        # محاسبه قیمت نهایی با توجه به تخفیف
        if self.is_active_discount and self.discount > 0:
            self.final_price = self.price - int((self.price * self.discount) / 100)
        else:
            self.final_price = self.price
            
        super().save(*args, **kwargs)

# مدل گالری محصول  product
class Gallery(models.Model):

    product = models.ForeignKey(Product,on_delete=models.CASCADE,verbose_name="محصول")

    image = models.ImageField(upload_to=upload_image_path,verbose_name="عکس", blank=True, null=True)

    class Meta :
        verbose_name ="عکس"
        verbose_name_plural = "گالری"
    
    def __str__(self):
        return f"{self.product}"
        
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.image and hasattr(self.image, 'path') and os.path.isfile(self.image.path):
            img = Image.open(self.image.path)
            output_size = (800, 800)
            img = img.resize(output_size, Image.LANCZOS)
            img.save(self.image.path)

