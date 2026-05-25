from django.contrib import admin
from django.contrib.auth.models import User
from .models import ClientAddress, Profile, Notification, FavouriteProducts, UserCoupon

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'پروفایل'
    verbose_name = 'پروفایل'

class CustomUserAdmin(admin.ModelAdmin):
    inlines = (ProfileInline,)

class ClientAddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'title_address', 'province', 'city', 'postcode')
    list_filter = ('province', 'city')
    search_fields = ('user__username', 'user__email', 'province', 'city', 'postcode', 'full_address')
    
    fieldsets = (
        ('کاربر', {
            'fields': ('user',)
        }),
        ('اطلاعات آدرس', {
            'fields': ('title_address', 'province', 'city', 'full_address', 'postcode')
        }),
    )

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'is_phone_verified')
    list_filter = ('is_phone_verified',)
    search_fields = ('user__username', 'user__email', 'phone_number')
    
    fieldsets = (
        ('کاربر', {
            'fields': ('user',)
        }),
        ('اطلاعات تلفن', {
            'fields': ('phone_number', 'is_phone_verified', 'verification_code', 'verification_code_created_at')
        }),
    )

class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'notification_type', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('user__username', 'title', 'message')
    
    fieldsets = (
        ('کاربر', {
            'fields': ('user',)
        }),
        ('اطلاعات اعلان', {
            'fields': ('title', 'message', 'notification_type', 'is_read', 'related_url')
        }),
    )

@admin.register(UserCoupon)
class UserCouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'user', 'discount', 'is_active', 'expire_at', 'created_at')
    list_filter = ('is_active', 'expire_at', 'created_at')
    search_fields = ('code', 'user__username', 'user__phone_number')

# Register your models here.
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
admin.site.register(ClientAddress, ClientAddressAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(Notification, NotificationAdmin)
admin.site.register(FavouriteProducts)