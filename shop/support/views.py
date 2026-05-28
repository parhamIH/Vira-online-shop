from django.shortcuts import render, redirect, get_object_or_404
from shop.utils.cart_utils import get_cart_info
from shop.utils.sms import send_sms  # فرض بر این است که چنین utility دارید
from shop.cart.models import Cart, CartItem
from django.contrib.auth.decorators import login_required
from shop.support.models import SupportTicket, TicketReply
from shop.account.models import Notification 
from shop.account.views import get_common_context
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.models import User
from django.db import models
from django.contrib.admin.views.decorators import staff_member_required

# Create your views here.


@login_required(login_url='/login/')
def support(request):
    # استفاده از get_common_context برای دریافت اطلاعات مشترک
    context = get_common_context(request)
    
    # بررسی وجود درخواست‌های POST
    if request.method == 'POST':
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        department = request.POST.get('department')
        priority = request.POST.get('priority')
        attachment = request.FILES.get('attachment', None)
        
        try:
            # ایجاد یک درخواست پشتیبانی جدید
            ticket = SupportTicket.objects.create(
                user=request.user,
                subject=subject,
                message=message,
                department=department,
                priority=priority,
                attachment=attachment,
                status='pending'
            )
            
            # ایجاد اعلان برای کاربر
            user_notification = Notification.objects.create(
                user=request.user,
                title='درخواست پشتیبانی ثبت شد',
                message=f'درخواست شما با موضوع "{subject}" با موفقیت ثبت شد و به زودی بررسی خواهد شد.',
                notification_type='info',
                is_read=False
            )
            
            # ایجاد اعلان برای ادمین
            admin_users = User.objects.filter(is_staff=True)
            for admin in admin_users:
                Notification.objects.create(
                    user=admin,
                    title='درخواست پشتیبانی جدید',
                    message=f'یک درخواست پشتیبانی جدید از کاربر {request.user.username} با موضوع "{subject}" دریافت شد.',
                    notification_type='info',
                    is_read=False
                )
            
            # ارسال SMS بعد از ثبت تیکت
            send_sms(request.user.profile.phone_number, f"تیکت شما با موضوع '{subject}' ثبت شد و به زودی بررسی می‌شود.")
            
            context['success_message'] = 'درخواست پشتیبانی شما با موفقیت ثبت شد.'
            
        except Exception as e:
            context['error_message'] = f'خطا در ثبت درخواست: {str(e)}'
    
    # اضافه کردن اطلاعات مربوط به تیکت‌های قبلی کاربر
    tickets = SupportTicket.objects.filter(user=request.user).order_by('-created_at')
    context['tickets'] = tickets
    context['tickets_all'] = tickets.count()
    context['tickets_pending'] = tickets.filter(status='pending').count()
    context['tickets_in_progress'] = tickets.filter(status='in_progress').count()
    context['tickets_resolved'] = tickets.filter(status='resolved').count()
    context['tickets_closed'] = tickets.filter(status='closed').count()
    
    return render(request, "frontend/template/support.html", context)

@login_required
@require_POST
def support_ajax(request):
    try:
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        department = request.POST.get('department')
        priority = request.POST.get('priority')
        attachment = request.FILES.get('attachment', None)
        
        # ایجاد یک درخواست پشتیبانی جدید
        ticket = SupportTicket.objects.create(
            user=request.user,
            subject=subject,
            message=message,
            department=department,
            priority=priority,
            attachment=attachment,
            status='pending'
        )
        
        # ایجاد اعلان برای کاربر
        user_notification = Notification.objects.create(
            user=request.user,
            title='درخواست پشتیبانی ثبت شد',
            message=f'درخواست شما با موضوع "{subject}" با موفقیت ثبت شد و به زودی بررسی خواهد شد.',
            notification_type='info',
            is_read=False
        )
        
        # ایجاد اعلان برای ادمین
        admin_users = User.objects.filter(is_staff=True)
        for admin in admin_users:
            Notification.objects.create(
                user=admin,
                title='درخواست پشتیبانی جدید',
                message=f'یک درخواست پشتیبانی جدید از کاربر {request.user.username} با موضوع "{subject}" دریافت شد.',
                notification_type='info',
                is_read=False
            )
        
        # شمارش تعداد اعلان‌های خوانده نشده
        unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
        
        # ارسال SMS بعد از ثبت تیکت
        send_sms(request.user.profile.phone_number, f"تیکت شما با موضوع '{subject}' ثبت شد و به زودی بررسی می‌شود.")
        
        return JsonResponse({
            'status': 'success',
            'message': 'درخواست پشتیبانی شما با موفقیت ثبت شد.',
            'unread_count': unread_count,
            'ticket_id': ticket.id
        })
    
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'خطا در ثبت درخواست: {str(e)}'
        }, status=400)


@login_required
def view_ticket(request, ticket_id):
    try:
        # اصلاح view برای دسترسی ادمین به تمام تیکت‌ها
        if request.user.is_staff:
            ticket = get_object_or_404(SupportTicket, id=ticket_id)
        else:
            ticket = get_object_or_404(SupportTicket, id=ticket_id, user=request.user)
            
        context = get_common_context(request)
        context['ticket'] = ticket
        
        # دریافت پاسخ‌های تیکت
        replies = TicketReply.objects.filter(ticket=ticket).order_by('created_at')
        context['replies'] = replies
        
        return render(request, "frontend/template/ticket_detail.html", context)
    except SupportTicket.DoesNotExist:
        return redirect('support')

@login_required
@require_POST
def close_ticket(request, ticket_id):
    try:
        ticket = get_object_or_404(SupportTicket, id=ticket_id, user=request.user)
        
        # فقط تیکت‌های باز را می‌توان بست
        if ticket.status != 'closed':
            ticket.status = 'closed'
            ticket.save()
            
            # ایجاد اعلان برای کاربر
            Notification.objects.create(
                user=request.user,
                title='تیکت بسته شد',
                message=f'تیکت شما با موضوع "{ticket.subject}" با موفقیت بسته شد.',
                notification_type='info',
                is_read=False
            )
            
            # اعلان برای ادمین‌ها
            admin_users = User.objects.filter(is_staff=True)
            for admin in admin_users:
                Notification.objects.create(
                    user=admin,
                    title='تیکت بسته شد',
                    message=f'تیکت با موضوع "{ticket.subject}" توسط کاربر {request.user.username} بسته شد.',
                    notification_type='info',
                    is_read=False
                )
            
            # ارسال SMS بعد از بسته شدن تیکت
            send_sms(request.user.profile.phone_number, f"تیکت با موضوع '{ticket.subject}' بسته شد.")
            
            return redirect('view_ticket', ticket_id=ticket.id)
        else:
            # اگر تیکت قبلاً بسته شده باشد
            return redirect('view_ticket', ticket_id=ticket.id)
        
    except Exception as e:
        return redirect('support')

@login_required
@require_POST
def add_reply(request, ticket_id):
    try:
        # اجازه ادمین برای پاسخ به تیکت‌های همه کاربران
        if request.user.is_staff:
            ticket = get_object_or_404(SupportTicket, id=ticket_id)
        else:
            ticket = get_object_or_404(SupportTicket, id=ticket_id, user=request.user)
        
        # اگر تیکت بسته شده باشد، امکان پاسخ وجود ندارد
        if ticket.status == 'closed':
            return JsonResponse({
                'status': 'error',
                'message': 'این تیکت بسته شده است و امکان ارسال پاسخ وجود ندارد.'
            }, status=400)
        
        message = request.POST.get('message')
        attachment = request.FILES.get('attachment', None)
        change_status = request.POST.get('change_status', None)
        
        # ایجاد پاسخ جدید
        reply = TicketReply.objects.create(
            ticket=ticket,
            user=request.user,
            message=message,
            attachment=attachment,
            is_staff_reply=request.user.is_staff  # تشخیص خودکار پاسخ کارمند
        )
        
        # اگر کاربر ادمین باشد و وضعیت را تغییر دهد
        if request.user.is_staff and change_status:
            ticket.status = change_status
            ticket.save()
        # اگر تیکت در وضعیت "در انتظار بررسی" باشد، به "در حال بررسی" تغییر وضعیت دهید
        elif ticket.status == 'pending' and not request.user.is_staff:
            ticket.status = 'in_progress'
            ticket.save()
        
        # ایجاد اعلان برای طرف مقابل
        if request.user.is_staff:
            # اگر پاسخ دهنده کارمند باشد، به کاربر اعلان ارسال شود
            Notification.objects.create(
                user=ticket.user,
                title='پاسخ جدید به تیکت شما',
                message=f'تیکت شما با موضوع "{ticket.subject}" پاسخ جدیدی دریافت کرد.',
                notification_type='info',
                is_read=False
            )
            
            # ارسال SMS بعد از ثبت پاسخ توسط ادمین
            send_sms(ticket.user.profile.phone_number, f"پاسخ جدیدی برای تیکت '{ticket.subject}' دریافت کردید.")
        else:
            # اگر پاسخ دهنده کاربر عادی باشد، به ادمین‌ها اعلان ارسال شود
            admin_users = User.objects.filter(is_staff=True)
            for admin in admin_users:
                Notification.objects.create(
                    user=admin,
                    title='پاسخ جدید به تیکت',
                    message=f'تیکت با موضوع "{ticket.subject}" از کاربر {ticket.user.username} پاسخ جدیدی دریافت کرد.',
                    notification_type='info',
                    is_read=False
                )
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # اگر درخواست Ajax باشد، پاسخ JSON برگردانید
            return JsonResponse({
                'status': 'success',
                'message': 'پاسخ شما با موفقیت ثبت شد.',
                'reply_id': reply.id,
                'reply_date': reply.created_at.strftime('%Y/%m/%d %H:%M'),
                'is_staff': reply.is_staff_reply
            })
        else:
            # در غیر این صورت، به صفحه جزئیات تیکت برگردید
            return redirect('view_ticket', ticket_id=ticket.id)
    
    except Exception as e:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'error',
                'message': f'خطا در ثبت پاسخ: {str(e)}'
            }, status=400)
        else:
            return redirect('view_ticket', ticket_id=ticket_id)

@login_required
@require_POST
def change_ticket_status(request, ticket_id, status):
    # فقط ادمین‌ها مجاز به تغییر مستقیم وضعیت هستند
    if not request.user.is_staff:
        return redirect('view_ticket', ticket_id=ticket_id)
        
    try:
        ticket = get_object_or_404(SupportTicket, id=ticket_id)
        
        # بررسی وضعیت معتبر
        valid_statuses = ['pending', 'in_progress', 'resolved', 'closed']
        if status not in valid_statuses:
            return redirect('view_ticket', ticket_id=ticket_id)
            
        # تغییر وضعیت
        ticket.status = status
        ticket.save()
        
        # ایجاد اعلان برای کاربر
        status_persian = {
            'pending': 'در انتظار بررسی',
            'in_progress': 'در حال بررسی',
            'resolved': 'حل شده',
            'closed': 'بسته شده'
        }
        
        Notification.objects.create(
            user=ticket.user,
            title='تغییر وضعیت تیکت',
            message=f'وضعیت تیکت شما با موضوع "{ticket.subject}" به "{status_persian[status]}" تغییر یافت.',
            notification_type='info',
            is_read=False
        )
        
        return redirect('view_ticket', ticket_id=ticket_id)
    except Exception as e:
        return redirect('view_ticket', ticket_id=ticket_id)

@login_required
def admin_tickets(request):
    # فقط ادمین‌ها مجاز به دسترسی هستند
    if not request.user.is_staff:
        return redirect('support')
    
    context = get_common_context(request)
    
    # فیلترهای وضعیت
    status_filter = request.GET.get('status', '')
    # فیلتر اولویت
    priority_filter = request.GET.get('priority', '')
    # فیلتر دپارتمان
    department_filter = request.GET.get('department', '')
    # جستجوی متنی
    search_query = request.GET.get('search', '')
    
    # پایه کوئری
    tickets = SupportTicket.objects.all().order_by('-created_at')
    
    # اعمال فیلترها
    if status_filter:
        tickets = tickets.filter(status=status_filter)
    if priority_filter:
        tickets = tickets.filter(priority=priority_filter)
    if department_filter:
        tickets = tickets.filter(department=department_filter)
    if search_query:
        tickets = tickets.filter(
            models.Q(subject__icontains=search_query) |
            models.Q(message__icontains=search_query) |
            models.Q(user__username__icontains=search_query)
        )
    
    # آمار کلی تیکت‌ها
    context['tickets'] = tickets
    context['tickets_all'] = SupportTicket.objects.count()
    context['tickets_pending'] = SupportTicket.objects.filter(status='pending').count()
    context['tickets_in_progress'] = SupportTicket.objects.filter(status='in_progress').count()
    context['tickets_resolved'] = SupportTicket.objects.filter(status='resolved').count()
    context['tickets_closed'] = SupportTicket.objects.filter(status='closed').count()
    
    # پارامترهای فیلتر برای حفظ وضعیت فیلترها در صفحه
    context['status_filter'] = status_filter
    context['priority_filter'] = priority_filter
    context['department_filter'] = department_filter
    context['search_query'] = search_query
    
    return render(request, "frontend/template/admin_tickets.html", context)

@staff_member_required
def send_custom_sms(request):
    context = {}
    if request.method == 'POST':
        phone = request.POST.get('phone')
        text = request.POST.get('text')
        if phone and text:
            success, response = send_sms(phone, text)
            if success:
                context['success'] = 'پیامک با موفقیت ارسال شد.'
            else:
                context['error'] = f'خطا در ارسال پیامک: {response}'
        else:
            context['error'] = 'شماره و متن پیامک الزامی است.'
    return render(request, 'frontend/template/send_sms.html', context)