from django.contrib import admin
from shop.public.models import *
from django.utils.html import format_html



class SizeAdmin(admin.ModelAdmin):
    list_display = ('size', 'size_numrical', 'category')
    search_fields = ('size', 'size_numrical')
    list_filter = ('category',)
    fieldsets = (
        ("اطلاعات سایز", {
            'fields': ('size', 'number_size', 'size_numrical', 'category')
        }),
    )


class BrandAdmin(admin.ModelAdmin):
    list_filter = ("category", "name")
    ordering = ("en_name",)
    list_editable = ("name",)
    list_display = ("en_name", "name", "logo_preview")
    list_display_links = ("en_name",)
    search_fields = ('name', 'en_name')
    
    def logo_preview(self, obj):
        if obj.logo:
            return format_html('<img src="{}" width="80" />', obj.logo.url)
        return "بدون لوگو"
    logo_preview.short_description = 'لوگو'
    
    fieldsets = (
        ("دسته بندی", {"fields": ('category',)}),
        ("نام ها", {'fields': ("en_name", "name")}),
        ("لوگو برند", {"fields": ('logo',)}),
    )


class BaseColorAdmin(admin.ModelAdmin):
    list_display = ('name', 'color_preview')
    search_fields = ('name',)
    
    def color_preview(self, obj):
        return format_html('<div style="background-color: {}; width: 30px; height: 30px; border-radius: 50%;"></div>', obj.color)
    color_preview.short_description = 'رنگ'
    
    fieldsets = (
        (None, {
            'fields': ('name', 'color')
        }),
    )


class ColorAdmin(admin.ModelAdmin):
    list_filter = ("base_color",)
    list_display = ("name", "hex_code", "hex_preview", "base_color", "image_preview")
    list_editable = ("hex_code",)
    list_display_links = ("name",)
    search_fields = ("name", "hex_code")
    
    def hex_preview(self, obj):
        return format_html('<div style="background-color: {}; width: 30px; height: 30px; border: 1px solid #ccc;"></div>', obj.hex_code)
    hex_preview.short_description = 'پیش‌نمایش'
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" />', obj.image.url)
        return "بدون تصویر"
    image_preview.short_description = 'تصویر'
    
    fieldsets = (
        ("رنگ", {"fields": ("name", "hex_code", "base_color")}),
        ("تصویر", {"fields": ("image",)}),
    )


# Register your models here.

admin.site.register(Size, SizeAdmin)
admin.site.register(BaseColor, BaseColorAdmin)
admin.site.register(Color, ColorAdmin)
admin.site.register(Brand, BrandAdmin)