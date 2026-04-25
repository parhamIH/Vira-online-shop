// فایل cart-fix.js - یک راه حل ساده برای مشکل شمارنده سبد خرید

(function() {
    // اجرا پس از بارگذاری صفحه
    document.addEventListener('DOMContentLoaded', function() {
        console.log('[CartFix] در حال راه‌اندازی...');
        setupCartDeletion();
    });

    // تنظیم رویدادهای حذف از سبد خرید
    function setupCartDeletion() {
        // یافتن دکمه‌های حذف
        var deleteButtons = document.querySelectorAll('[data-delete-item], .delete-cart-item, .remove-cart-item, .cart-delete');
        console.log('[CartFix] تعداد دکمه‌های حذف یافت شده:', deleteButtons.length);

        // اضافه کردن رویداد به هر دکمه
        deleteButtons.forEach(function(button) {
            button.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                
                // دریافت شناسه محصول
                var packageId = this.getAttribute('data-package-id') || this.getAttribute('data-id');
                if (!packageId) {
                    console.error('[CartFix] خطا: شناسه محصول یافت نشد');
                    return;
                }
                
                console.log('[CartFix] درخواست حذف محصول با شناسه:', packageId);
                
                // اجرای حذف بدون تأیید
                performCartDeletion(packageId, this);
            });
        });
    }

    // انجام عملیات حذف از سبد خرید
    function performCartDeletion(packageId, button) {
        console.log('[CartFix] شروع حذف محصول با شناسه:', packageId);
        
        // یافتن ردیف مربوط به محصول
        var row = button.closest('tr') || button.closest('.cart-item');
        if (row) {
            row.style.opacity = '0.5';
            console.log('[CartFix] ردیف محصول یافت شد و تغییر شفافیت اعمال شد');
        }

        // ایجاد درخواست
        var xhr = new XMLHttpRequest();
        xhr.open('POST', '/delete-cart-item/', true);
        xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
        xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
        
        // دریافت توکن CSRF
        var csrfToken = getCsrfToken();
        if (csrfToken) {
            xhr.setRequestHeader('X-CSRFToken', csrfToken);
            console.log('[CartFix] توکن CSRF یافت شد و به درخواست اضافه شد');
        } else {
            console.warn('[CartFix] توکن CSRF یافت نشد!');
        }

        // پس از دریافت پاسخ
        xhr.onload = function() {
            console.log('[CartFix] پاسخ دریافت شد با وضعیت:', xhr.status);
            
            if (xhr.status >= 200 && xhr.status < 300) {
                try {
                    var response = JSON.parse(xhr.responseText);
                    console.log('[CartFix] پاسخ دریافت شد:', response);
                    
                    // به‌روزرسانی شمارنده سبد خرید
                    var count = response.cart_items_count || response.cart_count || 0;
                    console.log('[CartFix] شمارنده جدید:', count);
                    updateAllCartCounters(count);
                    
                    // حذف ردیف
                    if (row) {
                        // اضافه کردن انیمیشن حذف
                        row.style.transition = 'all 0.5s';
                        row.style.height = '0';
                        row.style.opacity = '0';
                        row.style.overflow = 'hidden';
                        
                        // حذف کامل پس از اتمام انیمیشن
                        setTimeout(function() {
                            row.style.display = 'none';
                            console.log('[CartFix] ردیف محصول با موفقیت حذف شد');
                        }, 500);
                    }
                    
                    // به‌روزرسانی قیمت‌ها
                    updateCartPrices(response);
                    
                } catch (error) {
                    console.error('[CartFix] خطا در پردازش پاسخ:', error);
                    // بازگرداندن وضعیت ردیف به حالت عادی
                    if (row) {
                        row.style.opacity = '1';
                    }
                }
            } else {
                console.error('[CartFix] خطا در حذف محصول:', xhr.status, xhr.statusText);
                if (row) {
                    row.style.opacity = '1';
                }
            }
        };

        // در صورت خطا
        xhr.onerror = function() {
            console.error('[CartFix] خطا در ارتباط با سرور');
            if (row) {
                row.style.opacity = '1';
            }
        };

        // ارسال درخواست
        xhr.send('package_id=' + encodeURIComponent(packageId));
        console.log('[CartFix] درخواست حذف ارسال شد');
    }

    // به‌روزرسانی تمام شمارنده‌های سبد خرید در صفحه
    function updateAllCartCounters(count) {
        console.log('[CartFix] به‌روزرسانی شمارنده به:', count);
        
        // لیست تمام سلکتورهای ممکن برای شمارنده سبد خرید
        const selectors = [
            '#cartCounter',       // آیدی رایج
            '.cart-counter',      // کلاس رایج 
            '.cart-count',        // کلاس آلترناتیو
            '.header-cart-count', // احتمالاً در هدر
            '.cart-badge',        // بج سبد خرید
            '.basket-count',      // نام دیگر برای سبد خرید
            '[data-cart-count]'   // با استفاده از data attribute
        ];
        
        // جستجو و به‌روزرسانی تمام شمارنده‌ها
        selectors.forEach(selector => {
            const counters = document.querySelectorAll(selector);
            console.log(`[CartFix] ${counters.length} المان با سلکتور '${selector}' پیدا شد`);
            
            counters.forEach(counter => {
                // ذخیره مقدار قبلی
                const oldValue = counter.textContent.trim();
                
                // تنظیم مقدار جدید
                counter.textContent = count;
                
                // افزودن افکت بصری
                counter.style.transition = 'transform 0.3s, color 0.3s';
        // یافتن تمام شمارنده‌های ممکن
        var counters = document.querySelectorAll('#cartCounter, .cart-counter, .cart-count, .basket-count, [data-cart-count]');
        console.log('[CartFix] تعداد شمارنده‌های یافت شده:', counters.length);
        
        counters.forEach(function(counter) {
            // ذخیره مقدار قبلی
            var oldValue = counter.textContent.trim();
            
            // تنظیم مقدار جدید
            counter.textContent = count;
            
            // افزودن افکت بصری
            counter.style.transition = 'transform 0.3s';
            counter.style.transform = 'scale(1.3)';
            counter.style.color = '#ff0000';
            
            // بازگشت به حالت عادی
            setTimeout(function() {
                counter.style.transform = 'scale(1)';
                counter.style.color = '';
            }, 300);
        });
        
        // اگر هیچ شمارنده‌ای پیدا نشد، سعی کنید با ID تنظیم کنید
        if (counters.length === 0) {
            var navCount = document.getElementById('navbarSupportedContent');
            if (navCount) {
                var existingCounter = navCount.querySelector('.cart-counter');
                if (!existingCounter) {
                    var newCounter = document.createElement('span');
                    newCounter.className = 'cart-counter';
                    newCounter.textContent = count;
                    navCount.appendChild(newCounter);
                }
            }
        }
    }

    // به‌روزرسانی قیمت‌های سبد خرید
    function updateCartPrices(data) {
        // به‌روزرسانی قیمت کل
        if (data.total_price !== undefined) {
            var totalElements = document.querySelectorAll('.total-price, .cart-total');
            totalElements.forEach(function(el) {
                el.textContent = formatPrice(data.total_price) + ' تومان';
            });
        }
        
        // به‌روزرسانی قیمت کالاها
        if (data.total_goods_price !== undefined) {
            var goodsPriceElements = document.querySelectorAll('.total-goods-price');
            goodsPriceElements.forEach(function(el) {
                el.textContent = formatPrice(data.total_goods_price) + ' تومان';
            });
        }
        
        // به‌روزرسانی تخفیف
        if (data.total_discount !== undefined) {
            var discountElements = document.querySelectorAll('.total-discount');
            discountElements.forEach(function(el) {
                el.textContent = formatPrice(data.total_discount) + ' تومان';
            });
        }
    }

    // قالب‌بندی قیمت با کاما
    function formatPrice(price) {
        return price.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
    }

    // دریافت توکن CSRF
    function getCsrfToken() {
        var token = null;
        var tokenElement = document.querySelector('input[name="csrfmiddlewaretoken"]');
        if (tokenElement) {
            token = tokenElement.value;
        } else {
            // سعی در دریافت از کوکی
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = cookies[i].trim();
                if (cookie.startsWith('csrftoken=')) {
                    token = cookie.substring('csrftoken='.length, cookie.length);
                    break;
                }
            }
        }
        return token;
    }
})(); 