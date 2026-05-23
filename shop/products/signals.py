from django.db.models.signals import post_save
from django.dispatch import receiver
from guardian.shortcuts import assign_perm
from .models import ProductPackage

@receiver(post_save, sender=ProductPackage)
def give_permissions_to_provider(sender, instance, created, **kwargs):
    if created and instance.provider and instance.provider.user:
        user = instance.provider.user
        assign_perm('view_productpackage', user, instance)
        assign_perm('change_productpackage', user, instance)
        assign_perm('delete_productpackage', user, instance)
