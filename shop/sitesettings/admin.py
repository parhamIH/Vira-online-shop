from django.contrib import admin
from django.utils.html import format_html

from shop.sitesettings.models import SiteSettings


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ("site_name", "email", "phone", "logo_preview")

    fieldsets = (
        ("اطلاعات اصلی سایت", {
            "fields": ("site_name", "site_url", "logo", "favicon")
        }),
        ("اطلاعات تماس", {
            "fields": ("email", "phone", "address")
        }),
        ("شبکه‌های اجتماعی", {
            "fields": ("instagram", "telegram", "twitter", "linkedin")
        }),
        ("متن‌های سایت", {
            "fields": ("footer_text", "about_text")
        }),
        ("تنظیمات سئو", {
            "fields": ("seo_keywords", "seo_description")
        }),
        ("تنظیمات فروشگاه", {
            "fields": ("shipping_cost", "free_shipping_threshold", "tax_percentage")
        }),
    )

    def logo_preview(self, obj):
        if obj.logo:
            return format_html(
                '<img src="{}" width="120" style="border:1px solid #ccc;" />',
                obj.logo.url
            )
        return "بدون لوگو"

    logo_preview.short_description = "پیش‌نمایش لوگو"

    class Media:
        css = {
            "all": ("assets/css/admin-logo.css",)
        }
