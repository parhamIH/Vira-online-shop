from django.db import models
from django.contrib.auth.models import User

#__________________________________________ ------SupportTicket------ _______________________________________
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
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='support_tickets', verbose_name='client ')
    subject = models.CharField(max_length=255, verbose_name='subject')
    message = models.TextField(verbose_name='message')
    department = models.CharField(max_length=50, choices=DEPARTMENT_CHOICES, default='general', verbose_name='department')
    priority = models.CharField(max_length=50, choices=PRIORITY_CHOICES, default='medium', verbose_name='priority')
    attachment = models.FileField(upload_to='support_attachments/', null=True, blank=True, verbose_name="attachment")
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending', verbose_name='status')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='created_at')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='updated_at')
    
    class Meta:
        verbose_name = 'support ticket '
        verbose_name_plural = "support tickets"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.subject} - {self.user.username}"
    
#__________________________________________ ------TicketReply------ _______________________________________
class TicketReply(models.Model):
    ticket = models.ForeignKey('SupportTicket', on_delete=models.CASCADE, related_name='replies', verbose_name='ticket')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ticket_replies', verbose_name='client')
    message = models.TextField(verbose_name="message")
    attachment = models.FileField(upload_to='support_reply_attachments/', null=True, blank=True, verbose_name='attachment')
    is_staff_reply = models.BooleanField(default=False, verbose_name='is_staff_reply')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='created_at')
    
    class Meta:
        verbose_name = 'ticket response '
        verbose_name_plural =" ticket responses"
        ordering = ['created_at']
    
    def __str__(self):
        return f"پاسخ به {self.ticket.subject} - {self.user.username}"