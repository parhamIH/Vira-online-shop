from django.db import models
from django.contrib.auth.models import User

class SupportTicket(models.Model):
    STATUS_CHOICES = (
        ('pending', 'در انتظار بررسی'),
        ('in_progress', 'در حال بررسی'),
        ('resolved', 'حل شده'),
        ('closed', 'بسته شده'),
    )
    
    PRIORITY_CHOICES = (
        ('low', 'کم'),
        ('medium', 'متوسط'),
        ('high', 'زیاد'),
        ('urgent', 'فوری'),
    )
    
    DEPARTMENT_CHOICES = (
        ('general', 'عمومی'),
        ('technical', 'فنی'),
        ('billing', 'مالی'),
        ('sales', 'فروش'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='support_tickets', verbose_name='کاربر')
    subject = models.CharField(max_length=255, verbose_name='موضوع')
    message = models.TextField(verbose_name='پیام')
    department = models.CharField(max_length=50, choices=DEPARTMENT_CHOICES, default='general', verbose_name='دپارتمان')
    priority = models.CharField(max_length=50, choices=PRIORITY_CHOICES, default='medium', verbose_name='اولویت')
    attachment = models.FileField(upload_to='support_attachments/', null=True, blank=True, verbose_name='فایل پیوست')
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending', verbose_name='وضعیت')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='آخرین بروزرسانی')
    
    class Meta:
        verbose_name = 'تیکت پشتیبانی'
        verbose_name_plural = 'تیکت‌های پشتیبانی'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.subject} - {self.user.username}"

class TicketReply(models.Model):
    ticket = models.ForeignKey(SupportTicket, on_delete=models.CASCADE, related_name='replies', verbose_name='تیکت')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ticket_replies', verbose_name='کاربر')
    message = models.TextField(verbose_name='پیام')
    attachment = models.FileField(upload_to='support_reply_attachments/', null=True, blank=True, verbose_name='فایل پیوست')
    is_staff_reply = models.BooleanField(default=False, verbose_name='پاسخ کارمند')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    
    class Meta:
        verbose_name = 'پاسخ تیکت'
        verbose_name_plural = 'پاسخ‌های تیکت'
        ordering = ['created_at']
    
    def __str__(self):
        return f"پاسخ به {self.ticket.subject} - {self.user.username}"