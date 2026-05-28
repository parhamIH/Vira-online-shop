from django.db.models.signals import post_save
from django.dispatch import receiver
from guardian.shortcuts import assign_perm

from .models import Provider

@receiver(post_save, sender=Provider)
def set_user_as_staff(sender, instance, created, **kwargs):
    if created and not instance.user.is_staff:
        instance.user.is_staff = True
        instance.user.save()


@receiver(post_save, sender=Provider)
def assign_provider_permissions(sender, instance, created, **kwargs):

    if created:

        user = instance.user

        assign_perm("providers.manage_provider", user, instance)

        assign_perm("products.manage_own_products", user)

        assign_perm("products.manage_own_packages", user)