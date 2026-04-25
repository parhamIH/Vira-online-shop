// علامت‌گذاری یک اعلان به عنوان خوانده شده
function markAsRead(notificationId) {
    $.ajax({
        url: "{% url 'user_notifications' %}",
        type: "POST",
        data: {
            'notification_id': notificationId,
            'mark_read': true,
            'csrfmiddlewaretoken': csrftoken
        },
        headers: {
            "X-Requested-With": "XMLHttpRequest",
        },
        success: function(response) {
            if (response.status === 'success') {
                var notificationItem = $(`#notification-${notificationId}`);
                notificationItem.removeClass('unread').addClass('read');
                notificationItem.find('.border-start').removeClass('border-start border-4 border-primary');
                notificationItem.find('button[onclick^="markAsRead"]').remove();
                
                // به‌روزرسانی شمارنده اعلان‌های خوانده نشده
                updateUnreadCount();
                
                // نمایش پیام موفقیت
                showNotification('اعلان به عنوان خوانده شده علامت‌گذاری شد.', 'success');
            }
        }
    });
}

// علامت‌گذاری همه اعلان‌ها به عنوان خوانده شده
function markAllAsRead() {
    $.ajax({
        url: "{% url 'user_notifications' %}",
        type: "POST",
        data: {
            'mark_all_read': true,
            'csrfmiddlewaretoken': csrftoken
        },
        headers: {
            "X-Requested-With": "XMLHttpRequest",
        },
        success: function(response) {
            if (response.status === 'success') {
                $('.notification-item.unread').each(function() {
                    $(this).removeClass('unread').addClass('read');
                    $(this).find('.border-start').removeClass('border-start border-4 border-primary');
                    $(this).find('button[onclick^="markAsRead"]').remove();
                });
                
                // به‌روزرسانی شمارنده اعلان‌های خوانده نشده
                updateUnreadCount();
                
                // نمایش پیام موفقیت
                showNotification('همه اعلان‌ها به عنوان خوانده شده علامت‌گذاری شدند.', 'success');
            }
        }
    });
}

// حذف یک اعلان
function deleteNotification(notificationId) {
    $.ajax({
        url: "{% url 'user_notifications' %}",
        type: "POST",
        data: {
            'notification_id': notificationId,
            'delete_notification': true,
            'csrfmiddlewaretoken': csrftoken
        },
        headers: {
            "X-Requested-With": "XMLHttpRequest",
        },
        success: function(response) {
            if (response.status === 'success') {
                $(`#notification-${notificationId}`).fadeOut(300, function() {
                    $(this).remove();
                    
                    // بررسی خالی بودن لیست
                    if ($('.notification-item').length === 0) {
                        $('#notifications-container').html('<div class="col-12"><div class="alert alert-info">شما هیچ اعلان یا پیامی ندارید.</div></div>');
                    } else {
                        // بررسی خالی بودن نتایج فیلتر
                        checkEmptyResults();
                    }
                    
                    // به‌روزرسانی شمارنده اعلان‌های خوانده نشده
                    updateUnreadCount();
                });
                
                // نمایش پیام موفقیت
                showNotification('اعلان با موفقیت حذف شد.', 'success');
            }
        }
    });
}
