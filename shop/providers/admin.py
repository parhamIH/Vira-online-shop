from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.db.models import Sum

from .models import Provider, ProviderMember


# =========================
# ProviderMember Admin
# =========================

@admin.register(ProviderMember)
class ProviderMemberAdmin(admin.ModelAdmin):

    list_display = (
        'user',
        'provider',
        'is_owner',
        'is_active',
        'joined_at'
    )

    list_filter = (
        'is_active',
        'is_owner',
        'provider',
    )

    search_fields = (
        'user__username',
        'provider__company_name',
    )

    readonly_fields = (
        'joined_at',
    )

    # فقط اعضای Provider خودش را ببیند
    def get_queryset(self, request):

        qs = super().get_queryset(request)

        if request.user.is_superuser:
            return qs

        return qs.filter(
            provider__user=request.user
        )


# =========================
# Provider Admin
# =========================

@admin.register(Provider)
class ProviderAdmin(admin.ModelAdmin):

    list_display = (
        'company_name',
        'user',
        'provider_type',
        'status',
        'phone_number',
        'email',
        'is_verified',
        'is_active',
        'total_sales_count',
        'view_products_link',
    )

    list_filter = (
        'provider_type',
        'status',
        'is_verified',
        'is_active',
        'created_at',
    )

    search_fields = (
        'company_name',
        'legal_name',
        'user__username',
        'user__email',
        'phone_number',
        'national_id',
        'registration_number',
        'economic_code',
    )

    list_editable = (
        'status',
        'is_active',
    )

    readonly_fields = (
        'uuid',
        'created_at',
        'updated_at',
        'is_phone_verified',
        'verification_code',
        'verification_code_created_at',
        'total_sales_count',
        'email',
    )

    fieldsets = (

        ("اطلاعات اصلی", {
            'fields': (
                'company_name',
                'provider_type',
                'legal_name',
                'national_id',
                'registration_number',
                'economic_code',
            ),
            'classes': ('collapse',)
        }),

        ("اطلاعات تماس و حساب", {
            'fields': (
                'user',
                'email',
                'phone_number',
                'is_phone_verified',
                'website',
                'address',
                'city',
                'postal_code',
            ),
            'classes': ('collapse',)
        }),

        ("اطلاعات مالی", {
            'fields': (
                'sheba',
                'bank_account_number',
                'commission_rate',
            ),
            'classes': ('collapse',)
        }),

        ("وضعیت و نمایش", {
            'fields': (
                'status',
                'is_verified',
                'is_active',
                'logo',
                'description',
                'rating',
            )
        }),

        ("آمار", {
            'fields': (
                'total_sales_count',
            ),
            'classes': ('collapse',)
        }),

        ("زمان‌ها", {
            'fields': (
                'created_at',
                'updated_at',
            ),
            'classes': ('collapse',)
        }),
    )

    # =========================
    # SECURITY
    # =========================

    # فقط Provider خودش را ببیند
    def get_queryset(self, request):

        qs = super().get_queryset(request)

        if request.user.is_superuser:
            return qs

        return qs.filter(
            user=request.user
        )

    # جلوگیری از verify توسط provider
    def get_readonly_fields(self, request, obj=None):

        readonly = list(self.readonly_fields)

        if not request.user.is_superuser:

            readonly.extend([
                'is_verified',
                'status',
                'commission_rate',
                'rating',
                'user',
            ])

        return readonly

    # جلوگیری از edit provider دیگر
    def has_change_permission(self, request, obj=None):

        has_permission = super().has_change_permission(
            request,
            obj
        )

        if request.user.is_superuser:
            return has_permission

        if obj is None:
            return has_permission

        return obj.user == request.user

    # جلوگیری از delete provider دیگر
    def has_delete_permission(self, request, obj=None):

        if request.user.is_superuser:
            return True

        return False

    # جلوگیری از ساخت provider اضافی
    def has_add_permission(self, request):

        if request.user.is_superuser:
            return True

        # هر user فقط یک provider
        return not hasattr(
            request.user,
            'provider_profile'
        )

    # =========================
    # SALES
    # =========================

    def total_sales_count(self, obj):

        sales = obj.product_packages.aggregate(
            total_sold=Sum('sold_count')
        )

        return sales['total_sold'] or 0

    total_sales_count.short_description = 'مجموع فروش'

    # =========================
    # LINKS
    # =========================

    def view_products_link(self, obj):

        url = reverse(
            "admin:products_productpackage_changelist"
        )

        url += f"?provider__id__exact={obj.id}"

        return format_html(
            '<a href="{}" target="_blank">مشاهده پکیج‌ها</a>',
            url
        )

    view_products_link.short_description = 'پکیج‌ها'

    # =========================
    # LOGO
    # =========================

    def logo_preview(self, obj):

        if obj.logo:

            return format_html(
                '<img src="{}" width="50" height="50" />',
                obj.logo.url
            )

        return "بدون لوگو"

    logo_preview.short_description = 'لوگو'

