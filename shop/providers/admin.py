from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.db.models import Sum # برای محاسبه جمع فروش

from .models import Provider, ProviderMember

# کلاس ادمین برای ProviderMember (اگر نیاز به مدیریت اعضا هست)
@admin.register(ProviderMember)
class ProviderMemberAdmin(admin.ModelAdmin):
    list_display = ('user', 'provider', 'is_owner', 'is_active', 'joined_at')
    list_filter = ('is_active', 'is_owner', 'provider', 'user')
    search_fields = ('user__username', 'provider__company_name')
    readonly_fields = ('joined_at',)

# کلاس ادمین برای Provider
@admin.register(Provider)
class ProviderAdmin(admin.ModelAdmin):
    # نمایش اطلاعات کلیدی در لیست Providerها
    list_display = (
        'company_name', 
        'user', 
        'provider_type', 
        'status', 
        'phone_number', 
        'email', 
        'is_verified', 
        'is_active', 
        'total_sales_count', # متد کمکی برای نمایش فروش کل
        'view_products_link' # متد کمکی برای لینک محصولات
    )
    
    # فیلترها برای دسترسی سریع‌تر
    list_filter = (
        'provider_type', 
        'status', 
        'is_verified', 
        'is_active', 
        'created_at'
    )
    
    # فیلدهای قابل جستجو
    search_fields = (
        'company_name', 
        'legal_name', 
        'user__username', 
        'user__email', 
        'phone_number', 
        'national_id', 
        'registration_number', 
        'economic_code'
    )
    
    # فیلدهای قابل ویرایش مستقیم از لیست
    list_editable = ('status', 'is_active')
    
    # فیلدهای فقط خواندنی
    readonly_fields = (
        'uuid', 
        'created_at', 
        'updated_at', 
        'is_phone_verified', 
        'verification_code', 
        'verification_code_created_at',
        'total_sales_count', # اضافه کردن اینجا هم برای نمایش در فرم ویرایش
        'email' # ایمیل اصلی کاربر معمولا نباید از اینجا عوض شود
    )

    # دسته‌بندی فیلدها در صفحه ویرایش
    fieldsets = (
        ("اطلاعات اصلی", {
            'fields': ('company_name', 'provider_type', 'legal_name', 'national_id', 'registration_number', 'economic_code'),
             'classes': ('collapse',) # بسته‌بندی شده در حالت پیش‌فرض
        }),
        ("اطلاعات تماس و حساب", {
            'fields': ('user', 'email', 'phone_number', 'is_phone_verified', 'website', 'address', 'city', 'postal_code'),
            'classes': ('collapse',) # بسته‌بندی شده در حالت پیش‌فرض
        }),
        ("اطلاعات مالی", {
            'fields': ('sheba', 'bank_account_number', 'commission_rate'),
            'classes': ('collapse',)
        }),
        ("وضعیت و نمایش", {
            'fields': ('status', 'is_verified', 'is_active', 'logo', 'description', 'rating'),
        }),
        ("آمار", {
            'fields': ('total_sales_count',), # نمایش فروش کل
            'classes': ('collapse',)
        }),
        ("زمان‌ها", {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    # متد برای نمایش تعداد کل پکیج‌های فروخته شده (فروش کل)
    def total_sales_count(self, obj):
        # فرض بر اینکه مدل ProductPackage دارای فیلد 'sold_count' و relation به Provider است
        # اگر relation نام دیگری دارد، آن را اصلاح کنید
        sales = obj.product_packages.aggregate(total_sold=Sum('sold_count'))
        return sales['total_sold'] if sales['total_sold'] else 0
    total_sales_count.short_description = 'مجموع فروش (تعداد)'

    # متد برای نمایش لینک مستقیم به لیست محصولات آن Provider
    def view_products_link(self, obj):
        # مسیر تغییر نام یافته برای لیست پکیج‌ها (ProductPackageAdmin)
        # اگر نام app شما متفاوت است، آن را اصلاح کنید (مثلا 'yourappname_productpackage_changelist')
        url = reverse("admin:yourappname_productpackage_changelist") # نام app را اینجا وارد کنید
        url += f"?provider__id__exact={obj.id}" # فیلتر کردن بر اساس ID Provider
        return format_html(f'<a href="{url}" target="_blank">مشاهده پکیج‌ها</a>')
    view_products_link.short_description = 'پکیج‌ها'

    # برای اینکه بتونی از لیست، لوگوی آپلود شده رو ببینی
    def logo_preview(self, obj):
        if obj.logo:
            return format_html('<img src="{}" width="50" height="50" />', obj.logo.url)
        return "بدون لوگو"
    logo_preview.short_description = 'لوگو'

    # اضافه کردن logo_preview به list_display
    # list_display = ('company_name', ..., 'logo_preview', ...) # در ابتدای کلاس اضافه کنید

    # اگر از GuardedModelAdmin استفاده می‌کنید (برای مدیریت دسترسی‌های finer-grained)
    # class Media:
    #     css = {
    #         'all': ('path/to/your/custom.css',) # برای استایل‌های سفارشی
    #     }
    #     js = ('path/to/your/custom.js',) # برای جاوا اسکریپت سفارشی