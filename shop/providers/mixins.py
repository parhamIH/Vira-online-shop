from shop.providers.models import Provider
from shop.products.models import Product


class ProviderRestrictedAdminMixin:

    provider_field = 'provider'

    # =========================
    # QUERYSET SECURITY
    # =========================

    def get_queryset(self, request):

        qs = super().get_queryset(request)

        if request.user.is_superuser:
            return qs

        filter_kwargs = {
            f"{self.provider_field}__user": request.user
        }

        return qs.filter(**filter_kwargs)

    # =========================
    # CHANGE PERMISSION
    # =========================

    def has_change_permission(self, request, obj=None):

        has_permission = super().has_change_permission(
            request,
            obj
        )

        if request.user.is_superuser:
            return has_permission

        if obj is None:
            return has_permission

        provider = getattr(
            obj,
            self.provider_field,
            None
        )

        if not provider:
            return False

        return provider.user == request.user

    # =========================
    # DELETE PERMISSION
    # =========================

    def has_delete_permission(self, request, obj=None):

        if request.user.is_superuser:
            return True

        if obj is None:
            return False

        provider = getattr(
            obj,
            self.provider_field,
            None
        )

        if not provider:
            return False

        return provider.user == request.user

    # =========================
    # AUTO ASSIGN PROVIDER
    # =========================

    def save_model(self, request, obj, form, change):

        if not request.user.is_superuser:

            setattr(
                obj,
                self.provider_field,
                request.user.provider_profile
            )

        super().save_model(
            request,
            obj,
            form,
            change
        )

    # =========================
    # FOREIGNKEY SECURITY
    # =========================

    def formfield_for_foreignkey(
        self,
        db_field,
        request,
        **kwargs
    ):

        if not request.user.is_superuser:

            if db_field.name == "provider":

                kwargs["queryset"] = Provider.objects.filter(
                    user=request.user
                )

            if db_field.name == "product":

                kwargs["queryset"] = Product.objects.filter(
                    provider__user=request.user
                )

        return super().formfield_for_foreignkey(
            db_field,
            request,
            **kwargs
        )

