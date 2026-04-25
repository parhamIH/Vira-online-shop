function select_color_to_size(id, price) {
    document.getElementById('package-id').value = id;

    // اطمینان از اینکه قیمت یک عدد است
    const numericPrice = parseFloat(price);
    
    // فرمت کردن قیمت به عنوان رشته‌ی پولی
    const formattedPrice = numericPrice.toLocaleString('fa-IR') + '';
    document.getElementById('product-price').innerHTML = formattedPrice;

    // فیلتر کردن سایزهای مربوط به رنگ انتخاب شده
    var allSizeOptions = document.querySelectorAll('.size-option');
    var specificSizeOptions = document.querySelectorAll('.size-color-' + id);

    // مخفی کردن تمام گزینه‌های سایز
    allSizeOptions.forEach(function (el) {
        el.style.display = 'none';
    });

    // نمایش گزینه‌های سایز برای رنگ انتخاب شده
    specificSizeOptions.forEach(function (el) {
        el.style.display = 'block';
    });

    // به صورت خودکار انتخاب اولین گزینه سایز موجود برای رنگ انتخاب شده
    if (specificSizeOptions.length > 0) {
        specificSizeOptions[0].querySelector('input').checked = true;
    }
}   

// // بارگذاری اولیه
// document.addEventListener("DOMContentLoaded", function () {
//     var initialColorId = document.querySelector('input[name="color-options"]:checked').value;
//     select_color_to_size(initialColorId, document.querySelector('input[name="color-options"]:checked').getAttribute('data-price'));
// });
