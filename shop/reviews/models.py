from django.db import models
from shop.products.models import Product
from model_utils import FieldTracker  # Add this import
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.

class Comment(models.Model): 
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="کاربر")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="محصول")
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies', verbose_name="پاسخ به")
    text = models.TextField(verbose_name="متن نظر")
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], verbose_name="امتیاز")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="زمان ثبت")
    is_approved = models.BooleanField(default=False, verbose_name="تایید شده")
    
    # Add field tracker to track changes
    tracker = FieldTracker()

    class Meta:
        verbose_name = "نظر"
        verbose_name_plural = "نظرات"
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.user.username} - {self.product.name} - {self.rating}★"


