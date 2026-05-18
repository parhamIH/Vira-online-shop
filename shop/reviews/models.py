from django.db import models
from model_utils import FieldTracker  # Add this import
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User


# Create your models here.

#__________________________________________ ------Comment------ _______________________________________
class Comment(models.Model): 
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="client")
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE, verbose_name="product")
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies', verbose_name="response to")
    text = models.TextField(verbose_name="text")
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], verbose_name="rate")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="created_at")
    is_approved = models.BooleanField(default=False, verbose_name="is_approved")
    
    # Add field tracker to track changes
    tracker = FieldTracker()

    class Meta:
        verbose_name = "comment"
        verbose_name_plural = "comments"
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.user.username} - {self.product.name} - {self.rating} ★"


