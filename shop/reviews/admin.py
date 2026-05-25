from django.contrib import admin
from shop.reviews.models import *

# Register your models here.

class CommentAdmin(admin.ModelAdmin):
    readonly_fields = ("created_at",)
    list_display = ("product", "user", "created_at", "text_preview", "rating", "is_approved")
    list_display_links = ("product",)
    list_filter = ("product", "is_approved", "rating", "created_at")
    ordering = ("product", "created_at")
    list_editable = ("is_approved",)
    
    def text_preview(self, obj):
        if len(obj.text) > 50:
            return f"{obj.text[:50]}..."
        return obj.text
    text_preview.short_description = 'متن نظر'

    fieldsets = (
        ("محصول / کاربر", {"fields": ("product", "user")}),
        ("نظر / امتیاز", {"fields": ("text", "rating", "is_approved")}),
        ("زمان ثبت", {"fields": ("created_at",)}),
    )

admin.site.register(Comment, CommentAdmin)
