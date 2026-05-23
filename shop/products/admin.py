from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from .models import *
from django.utils.html import format_html
from guardian.admin import GuardedModelAdmin

### admin 

class GalleryInline(TabularInline):
    model = Gallery
    extra = 1

class GalleryAdmin(ModelAdmin):
    list_display = ["product", 'image_preview']
    list_display_links = ("product",)
    list_filter = ("product",)
    ordering = ("product",)

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" />', obj.image.url)
        return "بدون تصویر"
    image_preview.short_description = 'پیش‌نمایش تصویر'

    fieldsets = (
        ("محصول / عکس", {"fields": ("product", "image")}),
    )

class ProductPackageInline(TabularInline):
    model = ProductPackage
    extra = 1
    fields = ('size', 'brand', 'color', 'quantity', 'price', 'discount', 'is_active_discount', 'is_active_package', 'final_price')
    readonly_fields = ('final_price',)

    def get_queryset(self, request):
        # دریافت کوئری‌ست پایه
        qs = super().get_queryset(request)
        # اگر سوپریوزر است همه را ببیند، در غیر این صورت فقط بسته‌های خودش را ببیند
        if request.user.is_superuser:
            return qs
        return qs.filter(provider__user=request.user)


class ProductAdmin(ModelAdmin):
    inlines = [ProductPackageInline, GalleryInline]
    
    def get_categories(self, obj):
        return ", ".join([category.name for category in obj.categories.all()])
    get_categories.short_description = 'دسته‌بندی‌ها'
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="80" />', obj.image.url)
        return "بدون تصویر"
    image_preview.short_description = 'تصویر'

    readonly_fields = ("id", 'created_date', 'updated_date')
    search_fields = ["name", "description"]
    list_filter = ('is_active', "categories", "created_date")
    ordering = ("-created_date", "is_active")

    list_display = ("id", "name", "is_active", "get_categories", "created_date", "updated_date", "image_preview")
    list_editable = ("is_active",)
    list_display_links = ("name",)
    
    fieldsets = (
        ("نام محصول / توضیحات محصول / موجود", {"fields": ("name", "description", "is_active")}),
        ("دسته بندی", {"fields": ("categories",)}),
        ("تصویر محصول", {"fields": ("image",)}),
        ("زمان", {"fields": ("created_date", "updated_date")}),
    )

    def get_queryset(self, request):
        # دریافت کوئری‌ست پایه
        qs = super().get_queryset(request)
        # اگر سوپریوزر است همه محصولات را ببیند
        if request.user.is_superuser:
            return qs
        # در غیر این صورت فقط محصولاتی را ببیند که حداقل یک پکیج از این Provider دارند
        return qs.filter(product_packages__provider__user=request.user).distinct()


class ProductPackageAdmin(GuardedModelAdmin): # تغییر به GuardedModelAdmin
    list_display = ('product', 'size', 'brand', 'color', 'quantity', 'price', 'discount', 'final_price', 'is_active_discount', "is_active_package", "sold_count")
    search_fields = ('product__name', 'brand__name', 'color__name')
    list_filter = ('product', 'size', 'brand', 'is_active_discount', "is_active_package")
    ordering = ('product', 'size', "is_active_package")
    list_editable = ('is_active_discount', 'is_active_package', 'price', 'discount')
    readonly_fields = ('final_price', 'views_count', 'sold_count')
    
    fieldsets = (
        ("محصول و ویژگی‌ها", {'fields': ('product', 'size', 'brand', 'color')}),
        ("موجودی و وزن", {'fields': ('quantity', 'weight')}),
        ("قیمت‌گذاری", {'fields': ('price', 'discount', 'is_active_discount', 'final_price')}),
        ("وضعیت", {'fields': ('is_active_package',)}),
        ("آمار", {'fields': ('sold_count', 'views_count', 'rating')}),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        # محدود کردن به پکیج‌های متعلق به این provider
        return qs.filter(provider__user=request.user)

    def save_model(self, request, obj, form, change):
        if not request.user.is_superuser:
            # تخصیص خودکار provider هنگام ایجاد پکیج توسط خودش
            obj.provider = request.user.provider_profile 
        super().save_model(request, obj, form, change)


# Register your models here.
admin.site.register(ProductPackage, ProductPackageAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Gallery, GalleryAdmin)
