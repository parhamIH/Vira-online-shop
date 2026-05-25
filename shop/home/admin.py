from django.contrib import admin
from shop.home.models import *
from django.utils.html import format_html


class HomeSliderAdmin(admin.ModelAdmin):
    list_display = ('title', 'active', 'order', 'image_preview')
    list_filter = ('active',)
    list_editable = ('active', 'order')
    search_fields = ('title', 'subtitle')
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="150" />', obj.image.url)
        return "بدون تصویر"
    image_preview.short_description = 'تصویر'
    
    fieldsets = (
        ("عنوان و زیرعنوان", {
            'fields': ('title', 'subtitle')
        }),
        ("تصویر", {
            'fields': ('image',)
        }),
        ("لینک و وضعیت", {
            'fields': ('link', 'active', 'order')
        }),
    )


class PromotionalBannerAdmin(admin.ModelAdmin):
    list_display = ('title', 'position', 'size', 'active', 'order', 'image_preview')
    list_filter = ('active', 'position', 'size')
    list_editable = ('active', 'order', 'position', 'size')
    search_fields = ('title',)
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="150" />', obj.image.url)
        return "بدون تصویر"
    image_preview.short_description = 'تصویر'
    
    fieldsets = (
        ("عنوان", {
            'fields': ('title',)
        }),
        ("تصویر", {
            'fields': ('image',)
        }),
        ("موقعیت و اندازه", {
            'fields': ('position', 'size')
        }),
        ("لینک و وضعیت", {
            'fields': ('link', 'active', 'order')
        }),
    )


class FeaturedBrandAdmin(admin.ModelAdmin):
    list_display = ('brand', 'active', 'order', 'logo_preview')
    list_filter = ('active', 'brand')
    list_editable = ('active', 'order')
    
    def logo_preview(self, obj):
        if obj.brand.logo:
            return format_html('<img src="{}" width="80" />', obj.brand.logo.url)
        return "بدون لوگو"
    logo_preview.short_description = 'لوگو'

# Register your models here.

admin.site.register(HomeSlider, HomeSliderAdmin)
admin.site.register(PromotionalBanner, PromotionalBannerAdmin)
admin.site.register(FeaturedBrand, FeaturedBrandAdmin)