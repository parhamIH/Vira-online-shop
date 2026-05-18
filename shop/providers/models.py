import uuid
from django.db import models
from django.contrib.auth.models import User


#__________________________________________ ------Provider------ _______________________________________
class Provider(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE,related_name='provider_profile')

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    name = models.CharField(max_length=255)
    can_sell = models.BooleanField(default=True)

    address = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # فقط برای دسترسی ادمین
        self.user.is_staff = True
        self.user.save()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} - {self.user.username}"
