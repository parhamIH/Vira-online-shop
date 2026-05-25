from django.contrib import admin
from .models import SupportTicket, TicketReply

class TicketReplyInline(admin.TabularInline):
    model = TicketReply
    extra = 0
    readonly_fields = ('created_at',)
    fieldsets = (
        (None, {
            'fields': ('user', 'message', 'attachment', 'is_staff_reply', 'created_at')
        }),
    )

class SupportTicketAdmin(admin.ModelAdmin):
    list_display = ('id', 'subject', 'user', 'department', 'priority', 'status', 'created_at', 'updated_at')
    list_filter = ('status', 'department', 'priority', 'created_at')
    search_fields = ('subject', 'message', 'user__username', 'user__email')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'
    inlines = [TicketReplyInline]
    
    fieldsets = (
        (None, {
            'fields': ('user', 'subject', 'message', 'attachment')
        }),
        ('اطلاعات دسته‌بندی', {
            'fields': ('department', 'priority', 'status')
        }),
        ('اطلاعات زمانی', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # نمایش همه تیکت‌ها برای کاربران ادمین
        return qs
    
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        
        # اگر وضعیت تیکت تغییر کرده باشد، اعلان ایجاد کن
        if change and 'status' in form.changed_data:
            from account.models import Notification
            
            status_display = dict(SupportTicket.STATUS_CHOICES)[obj.status]
            Notification.objects.create(
                user=obj.user,
                title='تغییر وضعیت تیکت',
                message=f'وضعیت تیکت شما با موضوع "{obj.subject}" به "{status_display}" تغییر یافت.',
                type='info',
                is_read=False
            )

class TicketReplyAdmin(admin.ModelAdmin):
    list_display = ('id', 'ticket', 'user', 'is_staff_reply', 'created_at')
    list_filter = ('is_staff_reply', 'created_at')
    search_fields = ('message', 'user__username', 'ticket__subject')
    readonly_fields = ('created_at',)
    
    fieldsets = (
        (None, {
            'fields': ('ticket', 'user', 'message', 'attachment', 'is_staff_reply')
        }),
        ('اطلاعات زمانی', {
            'fields': ('created_at',)
        }),
    )
