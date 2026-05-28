from django.contrib import admin
from django.utils.html import format_html

from guardian.admin import GuardedModelAdmin

from .models import (
    Product,
    ProductPackage,
    Gallery,
)

from shop.providers.models import Provider

from .mixins import ProviderRestrictedAdminMixin


# =========================================================
# GALLERY INLINE
# =========================================================

class GalleryInline(admin.TabularInline):

    model = Gallery

    extra = 1


# =========================================================
# PRODUCT PACKAGE INLINE
# =========================================================

class ProductPackageInline(admin.TabularInline):

    model = ProductPackage

    extra = 1

    fields = (
        'size',
        'brand',
        'color',
        'quantity',
        'price',
        'discount',
        'is_active_discount',
        'is_active_package',
        'final_price',
    )

    readonly_fields = (
        'final_price',
    )

    # فقط پکیج‌های خودش را ببیند
    def get_queryset(self, request):

        qs = super().get_queryset(request)

        if request.user.is_superuser:
            return qs

        return qs.filter(
            provider__user=request.user
        )

    # محدود کردن provider
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

        return super().formfield_for_foreignkey(
            db_field,
            request,
            **kwargs
        )


# =========================================================
# GALLERY ADMIN
# =========================================================

@admin.register(Gallery)
class GalleryAdmin(admin.ModelAdmin):

    list_display = (
        "product",
        'image_preview',
    )

    list_display_links = (
        "product",
    )

    list_filter = (
        "product",
    )

    ordering = (
        "product",
    )

    fieldsets = (
        (
            "محصول / عکس",
            {
                "fields": (
                    "product",
                    "image",
                )
            }
        ),
    )

    def image_preview(self, obj):

        if obj.image:

            return format_html(
                '<img src="{}" width="100" />',
                obj.image.url
            )

        return "بدون تصویر"

    image_preview.short_description = 'پیش‌نمایش تصویر'

    # فقط گالری محصولات خودش
    def get_queryset(self, request):

        qs = super().get_queryset(request)

        if request.user.is_superuser:
            return qs

        return qs.filter(
            product__provider__user=request.user
        )


# =========================================================
# PRODUCT ADMIN
# =========================================================

@admin.register(Product)
class ProductAdmin(
    ProviderRestrictedAdminMixin,
    admin.ModelAdmin
):

    provider_field = 'provider'

    inlines = [
        ProductPackageInline,
        GalleryInline,
    ]

    readonly_fields = (
        "id",
        'created_date',
        'updated_date',
    )

    search_fields = (
        "name",
        "description",
    )

    list_filter = (
        'is_active',
        "categories",
        "created_date",
    )

    ordering = (
        "-created_date",
        "is_active",
    )

    list_display = (
        "id",
        "name",
        "provider",
        "is_active",
        "get_categories",
        "created_date",
        "updated_date",
        "image_preview",
    )

    list_editable = (
        "is_active",
    )

    list_display_links = (
        "name",
    )

    fieldsets = (

        (
            "اطلاعات محصول",
            {
                "fields": (
                    "provider",
                    "name",
                    "description",
                    "is_active",
                )
            }
        ),

        (
            "دسته بندی",
            {
                "fields": (
                    "categories",
                )
            }
        ),

        (
            "تصویر محصول",
            {
                "fields": (
                    "image",
                )
            }
        ),

        (
            "زمان",
            {
                "fields": (
                    "created_date",
                    "updated_date",
                )
            }
        ),
    )

    # فقط superuser بتواند provider تغییر دهد
    def get_readonly_fields(self, request, obj=None):

        readonly = list(self.readonly_fields)

        if not request.user.is_superuser:
            readonly.append("provider")

        return readonly

    # دسته بندی ها
    def get_categories(self, obj):

        return ", ".join([
            category.name
            for category in obj.categories.all()
        ])

    get_categories.short_description = 'دسته‌بندی‌ها'

    # تصویر
    def image_preview(self, obj):

        if obj.image:

            return format_html(
                '<img src="{}" width="80" />',
                obj.image.url
            )

        return "بدون تصویر"

    image_preview.short_description = 'تصویر'


# =========================================================
# PRODUCT PACKAGE ADMIN
# =========================================================

@admin.register(ProductPackage)
class ProductPackageAdmin(
    ProviderRestrictedAdminMixin,
    GuardedModelAdmin
):

    provider_field = 'provider'

    list_display = (
        'product',
        'provider',
        'size',
        'brand',
        'color',
        'quantity',
        'price',
        'discount',
        'final_price',
        'is_active_discount',
        "is_active_package",
        "sold_count",
    )

    search_fields = (
        'product__name',
        'brand__name',
        'color__name',
    )

    list_filter = (
        'product',
        'size',
        'brand',
        'is_active_discount',
        "is_active_package",
    )

    ordering = (
        'product',
        'size',
        "is_active_package",
    )

    list_editable = (
        'is_active_discount',
        'is_active_package',
        'price',
        'discount',
    )

    readonly_fields = (
        'final_price',
        'views_count',
        'sold_count',
    )

    fieldsets = (

        (
            "محصول و ویژگی‌ها",
            {
                'fields': (
                    'provider',
                    'product',
                    'size',
                    'brand',
                    'color',
                )
            }
        ),

        (
            "موجودی و وزن",
            {
                'fields': (
                    'quantity',
                    'weight',
                )
            }
        ),

        (
            "قیمت‌گذاری",
            {
                'fields': (
                    'price',
                    'discount',
                    'is_active_discount',
                    'final_price',
                )
            }
        ),

        (
            "وضعیت",
            {
                'fields': (
                    'is_active_package',
                )
            }
        ),

        (
            "آمار",
            {
                'fields': (
                    'sold_count',
                    'views_count',
                    'rating',
                )
            }
        ),
    )

    # فقط superuser بتواند provider تغییر دهد
    def get_readonly_fields(self, request, obj=None):

        readonly = list(self.readonly_fields)

        if not request.user.is_superuser:
            readonly.append("provider")

        return readonly
