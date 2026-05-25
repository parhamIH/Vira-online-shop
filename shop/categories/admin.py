from django.contrib import admin
from shop.categories.models import *
from mptt.admin import DraggableMPTTAdmin
from django.utils.html import format_html

@admin.register(BaseCategories)
class BaseCategoriesAdmin(admin.ModelAdmin):
    list_display = ("name", "en_name", "get_brands", "image_preview")
    list_filter = ("en_name", "name")
    ordering = ("name",)
    search_fields = ("name", "en_name")
    list_editable = ("en_name",)
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" />', obj.image.url)
        return "بدون تصویر"
    image_preview.short_description = 'تصویر'
    
    fieldsets = (
        ("نام ها", {'fields': ("en_name", "name")}),
        ("توضیحات دسته بندی", {"fields": ('description',)}),
        ("عکس دسته بندی", {"fields": ('image',)}),
    )
    list_select_related = True

    def get_brands(self, obj):
        return ", ".join([str(brand) for brand in obj.brands.all()])
    get_brands.short_description = 'برندها'




@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    mptt_indent_field = "name"
    list_display = ('parent', 'description',)
    search_fields = ['name', 'description']
    list_filter = ['parent']
