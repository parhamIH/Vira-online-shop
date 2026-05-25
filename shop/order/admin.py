from django.contrib import admin
from shop.order.models import Order
from django.utils.html import format_html
import jdatetime

# Register your models here.


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'user', 'status_colored', 'payment_status_colored', 'total_price', 'order_date_jalali', 'payment_date_jalali', 'shipping_method_display')
    list_filter = ('status', 'payment_status', 'payment_method', 'shipping_method', 'order_date')
    search_fields = ('order_number', 'user__username', 'user__email', 'payment_reference_id')
    readonly_fields = ('order_number', 'order_date', 'payment_date', 'payment_reference_id')
    ordering = ('-order_date',)
    
    fieldsets = (
        ('اطلاعات سفارش', {
            'fields': ('user', 'cart', 'address', 'order_number', 'order_date', 'status', 'shipping_method', 'shipping_cost', 'total_price')
        }),
        ('اطلاعات پرداخت', {
            'fields': ('payment_method', 'payment_status', 'payment_id', 'payment_date', 'payment_reference_id', 'payment_error')
        }),
        ('اطلاعات ارسال', {
            'fields': ('shipping_date', 'delivery_date', 'jalali_delivery_date', 'notes')
        }),
    )

    def order_date_jalali(self, obj):
        return jdatetime.datetime.fromgregorian(datetime=obj.order_date).strftime('%Y/%m/%d %H:%M')
    order_date_jalali.short_description = 'تاریخ سفارش'

    def payment_date_jalali(self, obj):
        if obj.payment_date:
            return jdatetime.datetime.fromgregorian(datetime=obj.payment_date).strftime('%Y/%m/%d %H:%M')
        return '-'
    payment_date_jalali.short_description = 'تاریخ پرداخت'

    def shipping_method_display(self, obj):
        return obj.get_shipping_method_display_name()
    shipping_method_display.short_description = 'روش ارسال'

    def total_price(self, obj):
        return f"{obj.total_price:,} تومان"
    total_price.short_description = 'مبلغ کل'
    
    def status_colored(self, obj):
        status_colors = {
            'در حال انتظار': 'orange',
            'تأیید شده': 'blue',
            'ارسال شده': 'purple',
            'تحویل داده شده': 'green',
            'لغو شده': 'red',
        }
        color = status_colors.get(obj.status, 'black')
        return format_html('<span style="color: {}; font-weight: bold;">{}</span>', color, obj.status)
    status_colored.short_description = 'وضعیت سفارش'
    
    def payment_status_colored(self, obj):
        status_colors = {
            'پرداخت شده': 'green',
            'در انتظار پرداخت': 'orange',
            'ناموفق': 'red',
            'لغو شده': 'red',
        }
        color = status_colors.get(obj.payment_status, 'black')
        return format_html('<span style="color: {}; font-weight: bold;">{}</span>', color, obj.payment_status)
    payment_status_colored.short_description = 'وضعیت پرداخت'