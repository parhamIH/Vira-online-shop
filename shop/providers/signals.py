from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Provider

@receiver(post_save, sender=Provider)
def set_user_as_staff(sender, instance, created, **kwargs):
    if created and not instance.user.is_staff:
        instance.user.is_staff = True
        instance.user.save()
