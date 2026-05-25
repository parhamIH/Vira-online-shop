from django.contrib import admin
from django.utils.html import format_html
from .models import Article

class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'short_description_display', 'image_preview', 'created_at', 'is_published')
    list_filter = ('is_published', 'created_at')
    search_fields = ('title', 'content', 'short_description')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('title', 'slug', 'short_description', 'content', 'image', 'is_published')
        }),
        ('اطلاعات SEO', {
            'fields': ('meta_title', 'meta_description', 'meta_keywords'),
            'classes': ('collapse',),
        }),
        ('تاریخ‌ها', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    
    def short_description_display(self, obj):
        if obj.short_description:
            return obj.short_description[:100] + '...' if len(obj.short_description) > 100 else obj.short_description
        return '-'
    short_description_display.short_description = 'توضیح کوتاه'
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 50px; max-width: 100px;" />', obj.image.url)
        return 'بدون تصویر'
    image_preview.short_description = 'پیش‌نمایش تصویر'
