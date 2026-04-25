$(document).ready(function() {
    // دریافت توکن CSRF از کوکی‌ها
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    const csrftoken = getCookie('csrftoken');

    // تنظیم عملکرد دکمه حذف
    $(document).on('click', '.delete-cart-item', function(e) {
        e.preventDefault(); // جلوگیری از رفتار پیش‌فرض دکمه

        var packageId = $(this).data('package-id'); // دریافت شناسه پکیج

        // درخواست AJAX برای حذف
        $.ajax({
            url: '/delete-cart-item/',
            type: 'POST',
            data: {
                'package_id': packageId,
                'csrfmiddlewaretoken': csrftoken // ارسال توکن CSRF به‌دست‌آمده از کوکی‌ها
            },
            success: function(response) {
                console.log('موفقیت:', response);

                // حذف عنصر مربوط به آیتم حذف‌شده
                $(e.target).closest('.cart-product-item, li.nav-item').remove();

                // به‌روزرسانی تعداد آیتم‌ها در سبد خرید
                if (response.cart_count !== undefined) {
                    $('#cartCounter').text(response.cart_count);
                    $('.text-muted.font-14.ms-1').text(response.cart_count);
                }

                // به‌روزرسانی قیمت کل
                if (response.total_price !== undefined) {
                    $('#total-price').text(response.total_price.toFixed(0));
                    $('.cart-canvas-foot-sum h5').text(response.total_price.toFixed(0) + ' تومان');
                }

                // نمایش صفحه سبد خرید خالی در صورت صفر شدن قیمت کل
                if (response.total_price === 0) {
                    $('.content').html('<div class="empty-cart text-center py-5">' +
                        '<h3>سبد خرید شما خالی است</h3>' +
                        '<p>لطفاً محصولات مورد نظر خود را به سبد خرید اضافه کنید.</p>' +
                        '<a href="/products" class="btn main-color-one-bg">بازگشت به فروشگاه</a>' +
                        '</div>');
                }
            },
            error: function(xhr, status, error) {
                console.log('خطا:', error);
            }
        });
    });
});
