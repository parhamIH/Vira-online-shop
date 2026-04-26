from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline, StackedInline
from shop.cart.models import Cart, CartItem
from shop.order.models import Order
from django.utils.html import format_html
from django.utils import timezone
import jdatetime

@admin.register(Cart)
class CartAdmin(ModelAdmin):
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

class CartItemAdmin(TabularInline):
    model = CartItem
    extra = 1
    fields = ('package', 'count', 'final_price', 'total_price')
    readonly_fields = ('final_price',)

    def total_price(self, obj):
        return f"{obj.total_price():,} تومان"
    total_price.short_description = 'قیمت کل'



@admin.register(Order)
class OrderAdmin(ModelAdmin):
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