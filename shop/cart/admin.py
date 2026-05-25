from django.contrib import admin
from shop.cart.models import Cart, CartItem
from django.utils.html import format_html
import jdatetime

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('cart_number', 'user', 'status', 'is_paid_colored', 'total_price', 'created_date_jalali', 'updated_date_jalali')
    list_filter = ('status', 'is_paid', 'created_date')
    search_fields = ('cart_number', 'user__username', 'user__email')
    readonly_fields = ('cart_number', 'created_date', 'updated_date')
    ordering = ('-created_date',)

    def created_date_jalali(self, obj):
        return jdatetime.datetime.fromgregorian(datetime=obj.created_date).strftime('%Y/%m/%d %H:%M')
    created_date_jalali.short_description = 'تاریخ ایجاد'

    def updated_date_jalali(self, obj):
        return jdatetime.datetime.fromgregorian(datetime=obj.updated_date).strftime('%Y/%m/%d %H:%M')
    updated_date_jalali.short_description = 'تاریخ به‌روزرسانی'

    def total_price(self, obj):
        return f"{obj.total_price():,} تومان"
    total_price.short_description = 'مبلغ کل'

    def is_paid_colored(self, obj):
        if obj.is_paid:
            return format_html('<span style="color: green; font-weight: bold;">پرداخت شده</span>')
        else:
            return format_html('<span style="color: red; font-weight: bold;">پرداخت نشده</span>')
    is_paid_colored.short_description = 'وضعیت پرداخت'

class CartItemAdmin(admin.TabularInline):
    model = CartItem
    extra = 1
    fields = ('package', 'count', 'final_price', 'total_price')
    readonly_fields = ('final_price',)

    def total_price(self, obj):
        return f"{obj.total_price():,} تومان"
    total_price.short_description = 'قیمت کل'

