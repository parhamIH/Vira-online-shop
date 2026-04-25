// این کد را در یک فایل جدید به نام cart-counter.js قرار دهید
// یا به فایل cart.js موجود اضافه کنید

document.addEventListener('DOMContentLoaded', function() {
    // بروزرسانی سبد خرید پس از حذف آیتم
    setupCartCounterUpdates();
});

// تابع اصلی برای راه‌اندازی بروزرسانی‌های شمارنده سبد خرید
function setupCartCounterUpdates() {
    // 1. یافتن تمام دکمه‌های حذف در صفحه سبد خرید
    const deleteButtons = document.querySelectorAll('.delete-cart-item, .remove-cart-item, .cart-remove-btn');
    
    // 2. افزودن گوش‌دهنده رویداد به هر دکمه
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const packageId = this.getAttribute('data-package-id');
            const cartForm = document.getElementById('cart-delete-form') || createHiddenForm();
            
            // تنظیم مقدار فرم و ارسال آن
            const packageIdInput = cartForm.querySelector('input[name="package_id"]');
            packageIdInput.value = packageId;
            
            // نمایش وضعیت درحال حذف
            const row = this.closest('tr') || this.closest('.cart-item');
            if (row) row.classList.add('deleting');
            
            // ارسال فرم با fetch برای جلوگیری از رفرش صفحه
            const formData = new FormData(cartForm);
            fetch(cartForm.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    // بروزرسانی شمارنده سبد خرید
                    updateCartCounterDisplay(data.cart_items_count || data.cart_count);
                    
                    // حذف ردیف از جدول
                    if (row) {
                        row.style.opacity = '0';
                        setTimeout(() => row.remove(), 300);
                    }
                    
                    // بروزرسانی قیمت‌ها
                    updateCartTotals(data);
                    
                    // نمایش پیام موفقیت
                    showMessage('محصول با موفقیت از سبد خرید حذف شد', 'success');
                } else {
                    // نمایش پیام خطا
                    showMessage(data.message || 'خطا در حذف محصول', 'error');
                    if (row) row.classList.remove('deleting');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showMessage('خطا در ارتباط با سرور', 'error');
                if (row) row.classList.remove('deleting');
            });
        });
    });
    
    // 3. یافتن تمام دکمه‌های کاهش که ممکن است به حذف منجر شوند
    const decreaseButtons = document.querySelectorAll('.decrease-btn');
    decreaseButtons.forEach(button => {
        button.addEventListener('click', function() {
            const counter = this.closest('.counter');
            const input = counter ? counter.querySelector('input') : null;
            if (input && parseInt(input.value) <= 1) {
                // زمانی که تعداد 1 است و کاربر دکمه کاهش را می‌زند
                const packageId = counter.getAttribute('data-package-id') || input.getAttribute('data-package-id');
                if (packageId) {
                    // ارسال درخواست حذف
                    deleteCartItem(packageId, counter);
                }
            }
        });
    });
}

// تابع حذف آیتم از سبد خرید
function deleteCartItem(packageId, element) {
    // ایجاد و تنظیم داده‌ها برای ارسال
    const formData = new FormData();
    formData.append('package_id', packageId);
    
    // ارسال درخواست به سرور
    fetch('/delete-cart-item/', {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': getCsrfToken()
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            // بروزرسانی شمارنده سبد خرید
            updateCartCounterDisplay(data.cart_items_count || data.cart_count);
            
            // تغییر وضعیت دکمه‌ها در صفحه محصول
            updateProductButtons(packageId);
            
            // نمایش پیام موفقیت
            showMessage('محصول با موفقیت از سبد خرید حذف شد', 'success');
        } else {
            // نمایش پیام خطا
            showMessage(data.message || 'خطا در حذف محصول', 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showMessage('خطا در ارتباط با سرور', 'error');
    });
}

// تابع بروزرسانی شمارنده سبد خرید
function updateCartCounterDisplay(count) {
    // یافتن تمام المان‌های شمارنده در صفحه
    const counters = document.querySelectorAll('#cartCounter, .cart-counter, .cart-count');
    
    // بروزرسانی متن شمارنده‌ها
    counters.forEach(counter => {
        // ذخیره مقدار قبلی برای افکت
        const oldValue = parseInt(counter.textContent) || 0;
        
        // تنظیم مقدار جدید
        counter.textContent = count;
        
        // افزودن کلاس برای افکت بصری
        counter.classList.add(oldValue > count ? 'decreased' : 'increased');
        
        // حذف کلاس پس از مدت کوتاهی
        setTimeout(() => {
            counter.classList.remove('decreased', 'increased');
        }, 1000);
        
        // پنهان کردن شمارنده اگر صفر است
        counter.style.display = count > 0 ? 'inline-block' : 'none';
    });
    
    // بروزرسانی عنوان صفحه (اختیاری)
    if (document.title.includes('(')) {
        document.title = document.title.replace(/\(\d+\)/, count > 0 ? `(${count})` : '');
    }
}

// تابع بروزرسانی قیمت‌های کل
function updateCartTotals(data) {
    // بروزرسانی قیمت کل
    if (data.total_price !== undefined) {
        document.querySelectorAll('.cart-total, .total-price').forEach(el => {
            el.textContent = formatPrice(data.total_price) + ' تومان';
        });
    }
    
    // بروزرسانی قیمت کل کالاها
    if (data.total_goods_price !== undefined) {
        document.querySelectorAll('.total-goods-price').forEach(el => {
            el.textContent = formatPrice(data.total_goods_price) + ' تومان';
        });
    }
    
    // بروزرسانی مجموع تخفیف
    if (data.total_discount !== undefined) {
        document.querySelectorAll('.total-discount').forEach(el => {
            el.textContent = formatPrice(data.total_discount) + ' تومان';
        });
    }
    
    // نمایش پیام سبد خرید خالی اگر نیاز است
    if ((data.cart_items_count === 0 || data.cart_count === 0) && document.querySelector('.cart-table')) {
        // بررسی اگر ردیفی در جدول باقی نمانده
        const remainingRows = document.querySelectorAll('.cart-table tbody tr:not(.deleting)');
        if (remainingRows.length === 0) {
            showEmptyCartMessage();
        }
    }
}

// تابع تغییر وضعیت دکمه‌ها در صفحه محصول
function updateProductButtons(packageId) {
    // دکمه افزودن به سبد خرید
    const addButton = document.querySelector(`button[data-package-id="${packageId}"]`);
    
    // کانتر در صفحه محصول
    const counter = document.querySelector(`.counter[data-package-id="${packageId}"]`);
    
    if (addButton && counter) {
        // نمایش دکمه افزودن به سبد خرید و مخفی کردن کانتر
        addButton.style.display = 'block';
        counter.style.display = 'none';
    }
}

// تابع نمایش پیام سبد خرید خالی
function showEmptyCartMessage() {
    const cartTable = document.querySelector('.cart-table');
    if (!cartTable) return;
    
    // مخفی کردن جدول سبد خرید
    cartTable.style.display = 'none';
    
    // مخفی کردن قسمت پرداخت
    const paymentSection = document.querySelector('.cart-summary, .checkout-section');
    if (paymentSection) paymentSection.style.display = 'none';
    
    // نمایش پیام سبد خرید خالی
    const emptyMessage = document.createElement('div');
    emptyMessage.className = 'empty-cart-message text-center py-5';
    emptyMessage.innerHTML = `
        <div class="mb-4"><i class="fas fa-shopping-cart fa-4x text-muted"></i></div>
        <h4 class="mb-3">سبد خرید شما خالی است</h4>
        <p class="mb-4">می‌توانید به فروشگاه بازگشته و محصولات مورد نظر خود را اضافه کنید</p>
        <a href="/shop/" class="btn btn-primary">مشاهده محصولات</a>
    `;
    
    // اضافه کردن پیام به صفحه
    cartTable.parentNode.insertBefore(emptyMessage, cartTable);
}

// تابع ایجاد فرم مخفی برای ارسال درخواست
function createHiddenForm() {
    const form = document.createElement('form');
    form.id = 'cart-delete-form';
    form.method = 'POST';
    form.action = '/delete-cart-item/';
    form.style.display = 'none';
    
    // افزودن فیلد package_id
    const packageIdInput = document.createElement('input');
    packageIdInput.type = 'hidden';
    packageIdInput.name = 'package_id';
    form.appendChild(packageIdInput);
    
    // افزودن توکن CSRF
    const csrfInput = document.createElement('input');
    csrfInput.type = 'hidden';
    csrfInput.name = 'csrfmiddlewaretoken';
    csrfInput.value = getCsrfToken();
    form.appendChild(csrfInput);
    
    // افزودن فرم به صفحه
    document.body.appendChild(form);
    
    return form;
}

// تابع دریافت توکن CSRF
function getCsrfToken() {
    const tokenElement = document.querySelector('input[name="csrfmiddlewaretoken"]');
    if (tokenElement) return tokenElement.value;
    
    const csrfCookie = document.cookie.split(';').find(c => c.trim().startsWith('csrftoken='));
    if (csrfCookie) return csrfCookie.split('=')[1];
    
    return '';
}

// تابع نمایش پیام
function showMessage(message, type) {
    // حذف پیام‌های قبلی
    const existingMessages = document.querySelectorAll('.cart-message');
    existingMessages.forEach(msg => msg.remove());
    
    // ایجاد المان پیام
    const messageElement = document.createElement('div');
    messageElement.className = `cart-message cart-message-${type}`;
    messageElement.textContent = message;
    
    // افزودن پیام به صفحه
    document.body.appendChild(messageElement);
    
    // نمایش پیام
    setTimeout(() => messageElement.classList.add('show'), 10);
    
    // حذف پیام پس از چند ثانیه
    setTimeout(() => {
        messageElement.classList.remove('show');
        setTimeout(() => messageElement.remove(), 300);
    }, 3000);
}

// تابع قالب‌بندی قیمت
function formatPrice(price) {
    return price.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}