// تعریف تابع filterSizes به صورت سراسری
function filterSizes(colorId) {
    console.log("فیلتر سایزها برای رنگ:", colorId);
    
    // مخفی کردن همه سایزها
    $(".size-option").hide();
    
    // نمایش سایزهای متناسب با رنگ انتخابی
    $(`.size-color-${colorId}`).show();
    
    // پاک کردن package-id فعلی
    $("#package-id").val("");
    
    // انتخاب اولین سایز موجود برای رنگ انتخابی
    const firstSizeInput = $(`.size-color-${colorId} input`).first();
    if (firstSizeInput.length) {
        // انتخاب اولین سایز
        firstSizeInput.prop("checked", true).trigger("click");
        
        // تنظیم package-id
        const packageId = firstSizeInput.val();
        setPackageId(packageId);
        
        // فعال کردن دکمه افزودن به سبد خرید
        $("#submit-button").prop("disabled", false);
    } else {
        // اگر هیچ سایزی برای این رنگ موجود نباشد
        console.warn("هیچ سایزی برای رنگ انتخابی موجود نیست");
        $("#submit-button").prop("disabled", true);
    }
}

// تابع جدید برای بروزرسانی قیمت محصول
function updateProductPrice(packageId) {
    // یافتن المان‌های قیمت
    const priceElement = $("#current-product-price");
    
    if (!priceElement.length) {
        console.warn("المان قیمت محصول یافت نشد");
        return;
    }
    
    // نمایش وضعیت بارگذاری
    priceElement.html(`
        <div class="d-flex align-items-center">
            <div class="spinner-border spinner-border-sm text-secondary me-2" role="status">
                <span class="visually-hidden">در حال بارگیری...</span>
            </div>
            <span>در حال دریافت قیمت...</span>
        </div>
    `);
    
    // دریافت اطلاعات پکیج از سرور
    fetch(`/get-package-info/${packageId}/`)
        .then(response => {
            if (!response.ok) {
                throw new Error('خطا در دریافت اطلاعات پکیج');
            }
            return response.json();
        })
        .then(data => {
            if (data.status === 'success' && data.package) {
                const price = data.package.price;
                const discountPrice = data.package.discount_price;
                const originalPrice = data.package.original_price;
                
                console.log("به‌روزرسانی قیمت محصول:", price, discountPrice);
                
                // بروزرسانی قیمت در المان product-price
                if (discountPrice && discountPrice < price) {
                    // قیمت اصلی را در المان parent (والد) نمایش می‌دهیم
                    priceElement.parent().prev(".text-decoration-line-through").text(numberWithCommas(originalPrice));
                    priceElement.text(numberWithCommas(discountPrice));
                } else {
                    // اگر تخفیف ندارد، خط قیمت اصلی را پنهان می‌کنیم
                    priceElement.parent().prev(".text-decoration-line-through").hide();
                    priceElement.text(numberWithCommas(price));
                }
                
                // به‌روزرسانی موجودی محصول اگر نیاز باشد
                if (data.package.quantity !== undefined) {
                    const maxQuantity = data.package.quantity;
                    $(".decrease-btn, .increase-btn, .counter-input").attr("data-max-quantity", maxQuantity);
                    $("input[name='count']").attr("max", maxQuantity).val(1);
                }
            } else {
                // نمایش خطا
                priceElement.html(`<span class="text-danger">خطا در دریافت قیمت</span>`);
                console.error("خطا در دریافت اطلاعات پکیج:", data.message);
            }
        })
        .catch(error => {
            // نمایش خطا
            priceElement.html(`<span class="text-danger">خطا در دریافت قیمت</span>`);
            console.error("خطا در دریافت اطلاعات پکیج:", error);
        });
}

// تعریف و مقداردهی اولیه cartManager
window.cartManager = {
    items: JSON.parse(localStorage.getItem('cartItems') || '[]'),
    
    saveToStorage: function() {
        localStorage.setItem('cartItems', JSON.stringify(this.items));
    },
    
    isInCart: function(packageId) {
        return this.items.some(item => item.package_id == packageId);
    },
    
    addItem: function(packageId, count) {
        if (!this.isInCart(packageId)) {
            this.items.push({ package_id: packageId, count: count });
            this.updateUI(packageId);
            this.saveToStorage();
            return true;
        }
        return false;
    },
    
    removeItem: function(packageId) {
        const initialLength = this.items.length;
        this.items = this.items.filter(item => item.package_id != packageId);
        
        if (initialLength > this.items.length) {
            this.updateUI(packageId);
            this.saveToStorage();
            return true;
        }
        return false;
    },
    
    updateUI: function(packageId) {
        const isInCart = this.isInCart(packageId);
        const submitButton = $("#submit-button");
        
        if (submitButton.length === 0) return;
        
        if (isInCart) {
            submitButton.prop("disabled", true);
            submitButton.addClass("in-cart");
            submitButton.text("در سبد خرید موجود است");
        } else {
            submitButton.prop("disabled", false);
            submitButton.removeClass("in-cart");
            submitButton.text("افزودن به سبد خرید");
        }
    },
    
    // همگام‌سازی با سرور
    syncWithServer: function() {
        fetch('/get-cart-content/')
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success' && data.cart_items) {
                    this.items = data.cart_items.map(item => ({
                        package_id: item.package_id,
                        count: item.count
                    }));
                    this.saveToStorage();
                    
                    // به‌روزرسانی UI اگر در صفحه جزئیات محصول هستیم
                    checkAndUpdateAddButton();
                }
            })
            .catch(error => console.error('خطا در همگام‌سازی سبد خرید:', error));
    }
};

// دریافت توکن CSRF
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
        document.cookie.split(";").forEach(cookie => {
            const [key, value] = cookie.trim().split("=");
            if (key === name) cookieValue = decodeURIComponent(value);
        });
    }
    return cookieValue;
}

// تابع تنظیم packageId
function setPackageId(packageId) {
    $("#package-id").val(packageId);
    $("#counter-package-id").val(packageId);
    
    const selectedSize = $(`#size-option${packageId}`);
    if (selectedSize.length) {
        const maxQuantity = selectedSize.data("quantity");
        $(".decrease-btn, .increase-btn, .counter-input").attr("data-max-quantity", maxQuantity);
        $(".counter-input").attr("data-package-id", packageId);
    }
    
    // بروزرسانی قیمت محصول با استفاده از packageId
    updateProductPrice(packageId);
}

// نمایش اعلان
function showAlert(message, type) {
    const alertBox = $(`<div class="custom-alert ${type}">${message}</div>`);
    $("body").append(alertBox);
    alertBox.fadeIn(300).delay(3000).fadeOut(500, function () {
        $(this).remove();
    });
}

// آماده‌سازی سند
$(document).ready(function () {
    console.log("آماده‌سازی سند...");
    
    // تابع بررسی حداکثر تعداد
    function checkMax(input) {
        const max = parseInt(input.max);
        let value = parseInt(input.value);
        if (value > max) {
            input.value = max;
            showAlert("❌ تعداد از موجودی بیشتر نمی‌تواند باشد!", "error");
        } else if (value < 1) {
            input.value = 1;
            showAlert("❌ تعداد نمی‌تواند کمتر از 1 باشد!", "error");
        }
    }
    
    // انتخاب اولین رنگ و اجرای فیلتر سایزها
    const initialColor = $(".color-option:checked").val();
    console.log("رنگ اولیه انتخابی:", initialColor);
    
    if (initialColor) {
        filterSizes(initialColor);
    } else {
        console.warn("هیچ رنگی به صورت پیش‌فرض انتخاب نشده است");
        
        // اگر هیچ رنگی انتخاب نشده، اولین رنگ را انتخاب می‌کنیم
        const firstColorInput = $(".color-option").first();
        if (firstColorInput.length) {
            firstColorInput.prop("checked", true);
            filterSizes(firstColorInput.val());
        }
    }
    
    // رویداد تغییر برای سایزها
    $(".size-option input").on("change", function () {
        console.log("تغییر سایز...");
        const packageId = $(this).val();
        setPackageId(packageId);
    });

    $("#add-to-cart-form").submit(function (e) {
        e.preventDefault();
        const userAuth = $("#login-status").data("authenticated");
        const packageId = $("#package-id").val();
        const count = $("input[name='count']").val();
        const csrfToken = getCookie("csrftoken");

        if (!packageId) {
            showAlert("❌ لطفاً رنگ و سایز را انتخاب کنید!", "error");
            return;
        }

        if (!userAuth) {
            showAlert("❌ لطفاً وارد شوید!", "error");
            setTimeout(() => window.location.href = "/login", 1000);
            return;
        }

        // نمایش وضعیت در حال بارگذاری
        const submitButton = $("#submit-button");
        const originalText = submitButton.text();
        submitButton.prop("disabled", true).text("در حال افزودن...");

        $.ajax({
            type: "POST",
            url: "/add-to-cart/",
            data: { 
                "package-id": packageId, 
                "count": count, 
                "csrfmiddlewaretoken": csrfToken 
            },
            success: function (response) {
                // بازگرداندن دکمه به حالت عادی
                submitButton.prop("disabled", false).text(originalText);
                
                // افزودن آیتم به cartManager محلی
                window.cartManager.addItem(packageId, count);
                
                // بروزرسانی شمارنده
                updateCartCounter(response.cart_items_count || 0);
                
                // بروزرسانی محتوای سبد خرید
                if (typeof updateCartContentManually === 'function' && response.cart_items) {
                updateCartContentManually(response.cart_items);
                } else {
                    // اگر تابع یا داده‌ها موجود نبود، از API دیگر استفاده کنیم
                    updateCartContent();
                }
                
                showAlert("✅ محصول به سبد خرید اضافه شد!", "success");
            },
            error: function (xhr, status, error) {
                // بازگرداندن دکمه به حالت عادی
                submitButton.prop("disabled", false).text(originalText);
                
                console.error("خطا در افزودن به سبد خرید:", error);
                console.log("وضعیت پاسخ:", xhr.status);
                console.log("متن پاسخ:", xhr.responseText);
                
                let errorMessage = "❌ خطا در افزودن به سبد خرید!";
                
                try {
                    const response = JSON.parse(xhr.responseText);
                    if (response.message) {
                        errorMessage = "❌ " + response.message;
                    } else if (response.error) {
                        errorMessage = "❌ " + response.error;
                    }
                } catch (e) {
                    // در صورت خطا در تجزیه JSON، از پیام پیش‌فرض استفاده می‌کنیم
                }
                
                showAlert(errorMessage, "error");
                
                // اگر خطای 401 بود، کاربر لاگین نشده است
                if (xhr.status === 401) {
                    setTimeout(() => window.location.href = "/login", 1500);
                }
            }
        });
    });

    // اضافه کردن رویداد تغییر برای رنگ‌ها
    $(".color-option").on("change", function() {
        const colorId = $(this).val();
        if (colorId) {
            filterSizes(colorId);
        }
    });

    const initialPackageId = $("#package-id").val();
    if (initialPackageId && window.cartManager.items.length > 0) {
        window.cartManager.updateUI(initialPackageId);
    }
    
    $("#package-id").change(function() {
        const newPackageId = $(this).val();
        window.cartManager.updateUI(newPackageId);
    });

    // همگام‌سازی cartManager با سرور
    window.cartManager.syncWithServer();

    // افزودن رویداد به دکمه‌های حذف در offcanvas
    $(document).on('click', '.delete-cart-item, .cart-canvas-delete .btn', function(e) {
        e.preventDefault();
        const packageId = $(this).data('package-id');
        if (packageId) {
            removeFromCart(packageId);
        }
    });

    // بررسی دکمه افزودن به سبد خرید
    checkAndUpdateAddButton();
    
    // همچنین این را به رویداد تغییر package-id اضافه کنیم
    $("#package-id").on('change', function() {
        checkAndUpdateAddButton();
    });
});

document.addEventListener("DOMContentLoaded", function () {
    const decreaseButtons = document.querySelectorAll(".decrease-btn");
    const increaseButtons = document.querySelectorAll(".increase-btn");

    decreaseButtons.forEach(button => {
        button.addEventListener("click", function (e) {
            e.preventDefault();
            const counterContainer = this.closest('.counter');
            const inputField = counterContainer.querySelector(".counter-input");
            const currentValue = parseInt(inputField.value) || 1;
            if (currentValue > 1) {
                inputField.value = currentValue - 1;
                updateCart(inputField, currentValue - 1);
            }
        });
    });

    increaseButtons.forEach(button => {
        button.addEventListener("click", function (e) {
            e.preventDefault();
            const counterContainer = this.closest('.counter');
            const inputField = counterContainer.querySelector(".counter-input");
            const maxQuantity = parseInt(this.dataset.maxQuantity || 100);
            const currentValue = parseInt(inputField.value) || 1;
            if (currentValue < maxQuantity) {
                inputField.value = currentValue + 1;
                updateCart(inputField, currentValue + 1);
            } else {
                showAlert("❌ موجودی محصول کافی نیست!", "error");
            }
        });
    });

    document.querySelectorAll(".counter-input").forEach(input => {
        input.addEventListener("change", function() {
            const value = parseInt(this.value) || 1;
            const max = parseInt(this.max) || 100;
            const min = parseInt(this.min) || 1;
            const newValue = Math.min(Math.max(value, min), max);
            this.value = newValue;
            updateCart(this, newValue);
        });
    });
});

function updateCart(inputField, newCount) {
    const packageId = inputField.dataset.packageId;
    if (!packageId) {
        console.error("خطا: شناسه پکیج وجود ندارد!");
        return;
    }

    // تغییر فوری مقدار ورودی برای تجربه کاربری بهتر
    inputField.value = newCount;
    const counterContainer = inputField.closest('.counter');
    if (counterContainer) {
        counterContainer.classList.add('updating');
    }

    fetch("/update-cart-item/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken")
        },
        body: JSON.stringify({ package_id: packageId, count: newCount })
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(data => {
                throw new Error(data.message || "خطا در به‌روزرسانی سبد خرید");
            });
        }
        return response.json();
    })
    .then(data => {
        if (counterContainer) {
            counterContainer.classList.remove('updating');
        }
        if (data.status === "success") {
            // به‌روزرسانی مقدار ورودی با داده‌های سرور
            inputField.value = data.count;
            
            // به‌روزرسانی شمارنده سبد خرید
            updateCartCounter(data.cart_items_count);
            
            // به‌روزرسانی قیمت‌ها
            updatePrices(data);
            
            // به‌روزرسانی محتوای سبد خرید
            if (data.cart_items) {
                // اگر سرور کل محتوای سبد خرید را برگرداند
                updateCartContentManually(data.cart_items);
            } else {
                // اگر سرور فقط اطلاعات آیتم به‌روز شده را برگرداند
                // به‌روزرسانی در cartManager
                if (window.cartManager) {
                    const itemIndex = window.cartManager.items.findIndex(item => item.package_id == packageId);
                    if (itemIndex !== -1) {
                        window.cartManager.items[itemIndex].count = data.count;
                        window.cartManager.saveToStorage();
                    }
                }
                
                // درخواست جداگانه برای دریافت محتوای به‌روز شده سبد خرید
                fetch('/get-cart-content/')
                    .then(response => response.json())
                    .then(cartData => {
                        if (cartData.status === 'success' && cartData.cart_items) {
                            updateCartContentManually(cartData.cart_items);
                        }
                    })
                    .catch(error => console.error("خطا در دریافت محتوای سبد خرید:", error));
            }
            
            showAlert("✅ سبد خرید به‌روزرسانی شد", "success");
        } else {
            // در صورت خطا، برگرداندن مقدار قبلی
            inputField.value = parseInt(inputField.value) || 1;
            showAlert("❌ " + (data.message || "خطا در به‌روزرسانی سبد خرید"), "error");
        }
    })
    .catch(error => {
        if (counterContainer) {
            counterContainer.classList.remove('updating');
        }
        // در صورت خطا، برگرداندن مقدار قبلی
        inputField.value = parseInt(inputField.value) || 1;
        showAlert("❌ " + (error.message || "خطا در به‌روزرسانی سبد خرید"), "error");
        console.error("خطای به‌روزرسانی سبد خرید:", error);
    });
}

// بهبود تابع بروزرسانی کانتر سبد خرید
function updateCartCounter(count) {
    // لیست سلکتورهای ممکن برای شمارنده سبد خرید
    const selectors = [
        '#cartCounter',
        '.cart-counter',
        '.cart-count',
        '.cart-badge',
        '[data-cart-count]'
    ];
    
    // یافتن و بروزرسانی تمام شمارنده‌های ممکن
    selectors.forEach(selector => {
        const elements = document.querySelectorAll(selector);
        elements.forEach(element => {
            element.textContent = count;
            // اضافه کردن کلاس برای نمایش انیمیشن
            element.classList.add('updated-count');
        setTimeout(() => {
                element.classList.remove('updated-count');
        }, 1000);
        });
    });
}

// فراخوانی جامع برای بروزرسانی سبد خرید
function refreshCartUI(data) {
    // بروزرسانی شمارنده
    if (data.cart_items_count !== undefined) {
        updateCartCounter(data.cart_items_count);
    }
    
    // بروزرسانی محتوای سبد خرید
    if (data.cart_items) {
        updateCartContentManually(data.cart_items);
    }
    
    // بروزرسانی قیمت‌ها
    updatePrices(data);
    
    // اگر سبد خرید خالی شد
    if (data.cart_items_count === 0) {
        if (typeof showEmptyCartMessage === 'function') {
            showEmptyCartMessage();
        }
    }
}

// تابع بروزرسانی محتوای سبد خرید به صورت دستی - با توجه به ساختار HTML شما
function updateCartContentManually(cartItems) {
    if (!cartItems || !Array.isArray(cartItems)) {
        console.error("داده‌های نامعتبر دریافت شده برای سبد خرید:", cartItems);
        return;
    }
    
    console.log("در حال بروزرسانی سبد خرید با", cartItems.length, "محصول");
    
    // یافتن کانتینر سبد خرید در Offcanvas
    const cartContainer = document.querySelector('.offcanvas-body .navbar-nav.cart-canvas-parent');
    if (!cartContainer) {
        console.error("کانتینر سبد خرید یافت نشد");
        return;
    }
    
    // بروزرسانی عنوان سبد خرید با تعداد محصولات
    const cartTitle = document.querySelector('#offcanvasCartLabel');
    if (cartTitle) {
        cartTitle.innerHTML = `سبد خرید <small class="text-muted font-14 ms-1">(${cartItems.length} مورد)</small>`;
    }
    
    // پاک کردن محتوای فعلی سبد خرید
    cartContainer.innerHTML = '';
    
    // اگر سبد خرید خالی است
    if (cartItems.length === 0) {
        cartContainer.innerHTML = `
            <li class="nav-item text-center p-4">
                <div class="empty-cart">
                    <i class="bi bi-basket font-50 text-muted"></i>
                    <p class="mt-3">سبد خرید شما خالی است</p>
                </div>
            </li>
        `;
        
        // بروزرسانی قیمت کل به صفر
        const totalPriceElement = document.querySelector('.cart-canvas-foot-sum h5');
        if (totalPriceElement) {
            totalPriceElement.textContent = '0 تومان';
        }
        
        return;
    }
    
    // محاسبه مجموع قیمت
    let totalPrice = 0;
    
    // افزودن محصولات به سبد خرید
    cartItems.forEach(item => {
        const itemPrice = item.price * item.count;
        totalPrice += itemPrice;
        
        // ساخت HTML برای هر محصول با توجه به ساختار موجود در _Main.html
        const itemHTML = `
            <li class="nav-item">
                <div class="cart-canvas">
                    <div class="row align-items-center">
                        <div class="col-4 ps-0">
                            <img src="${item.image || '/static/assets/img/placeholder.jpg'}" alt="${item.name || 'محصول'}">
                        </div>
                        <div class="col-8">
                            <a href="/product/${item.product_id || ''}">
                                <h3 class="text-overflow-1 title-font font-14">${item.name || 'محصول'}</h3>
                                <div class="cart-canvas-price my-3 d-flex align-items-center">
                                    ${item.discount_price ? 
                                        `<p class="mb-0 text-muted me-2 font-16 text-decoration-line-through">${numberWithCommas(item.original_price)} تومان</p>
                                        <h6 class="title-font main-color-one-color">${numberWithCommas(item.price)} تومان</h6>` 
                                        : 
                                        `<h6 class="title-font main-color-one-color">${numberWithCommas(item.price)} تومان</h6>`
                                    }
                                </div>
                            </a>
                            <div class="cart-canvas-foot d-flex align-items-center justify-content-between">
                                <div class="cart-canvas-count">
                                    <span>تعداد:</span>
                                    <span class="fw-bold main-color-one-color">${item.count}</span>
                                </div>
                                <div class="cart-canvas-delete">
                                    <button class="btn delete-cart-item" data-package-id="${item.package_id}"><i class="bi bi-x"></i></button>
                                </div>
                            </div>
                        </div>
                    </div>
            </div>
            </li>
        `;
        
        cartContainer.innerHTML += itemHTML;
    });
    
    // بروزرسانی قیمت کل
    const totalPriceElement = document.querySelector('.cart-canvas-foot-sum h5');
    if (totalPriceElement) {
        totalPriceElement.textContent = `${numberWithCommas(totalPrice)} تومان`;
    }
    
    // اضافه کردن رویداد کلیک به دکمه‌های حذف
    document.querySelectorAll('.delete-cart-item, .cart-canvas-delete .btn').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const packageId = this.dataset.packageId;
            if (packageId) {
                removeFromCart(packageId);
            }
        });
    });
}

// تابع کمکی برای فرمت کردن اعداد با کاما
function numberWithCommas(x) {
    return x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

// افزودن رویدادهای کلیک به دکمه‌های حذف
document.addEventListener('DOMContentLoaded', function() {
    console.log("راه‌اندازی رویدادهای دکمه حذف سبد خرید");
    
    // دکمه‌های حذف در سبد خرید
    const deleteButtons = document.querySelectorAll('.delete-cart-item, .remove-cart-item, .cart-remove-btn');
    console.log("تعداد دکمه‌های حذف یافت شده:", deleteButtons.length);
    
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            const packageId = this.dataset.packageId;
            console.log("کلیک روی دکمه حذف - package_id:", packageId);
            
            if (packageId) {
                // پرسیدن تأیید از کاربر (اختیاری)
                    removeFromCart(packageId);
                
            } else {
                console.error("خطا: شناسه پکیج (package_id) یافت نشد");
            }
        });
    });
});

// تابع جدید بروزرسانی شمارنده سبد خرید - سازگار با تمام سلکتورهای احتمالی
function updateHeaderCartCount(count) {
    console.log("------- بروزرسانی شمارنده سبد خرید به:", count, "-------");
    
    // لیست تمام سلکتورهایی که ممکن است برای شمارنده سبد خرید استفاده شده باشند
    const selectors = [
        '#cartCounter',       // آیدی رایج
        '.cart-counter',      // کلاس رایج 
        '.cart-count',        // کلاس آلترناتیو
        '.header-cart-count', // احتمالاً در هدر
        '.cart-badge',        // بج سبد خرید
        '.basket-count',      // نام دیگر برای سبد خرید
        '[data-cart-count]'   // با استفاده از data attribute
    ];
    
    // یافتن تمام المان‌های شمارنده با استفاده از همه سلکتورهای ممکن
    selectors.forEach(selector => {
        const elements = document.querySelectorAll(selector);
        if (elements.length > 0) {
            console.log(`${elements.length} المان با سلکتور '${selector}' پیدا شد`);
            
            elements.forEach((element, index) => {
                // بروزرسانی متن المان
                element.textContent = count;
                
                // اضافه کردن کلاس برای نمایش انیمیشن
                element.classList.add('updated-count');
                
                // حذف کلاس پس از اتمام انیمیشن
                setTimeout(() => {
                    element.classList.remove('updated-count');
                }, 1000);
                
                console.log(`المان شمارنده #${index+1} با سلکتور '${selector}' به ${count} بروزرسانی شد`);
            });
        }
    });
    
    // برای اطمینان بیشتر، یک المان جدید ایجاد می‌کنیم اگر هیچ المانی یافت نشد
    const allCounters = document.querySelectorAll(selectors.join(','));
    if (allCounters.length === 0) {
        console.log("هیچ شمارنده‌ای در صفحه یافت نشد. در حال ایجاد یک المان جدید...");
        
        // یافتن منوی اصلی یا هدر سایت
        const header = document.querySelector('header') || document.querySelector('nav') || document.body;
        
        // ایجاد یک شمارنده جدید
        const newCounter = document.createElement('span');
        newCounter.id = 'cartCounter';
        newCounter.className = 'cart-counter updated-count';
        newCounter.textContent = count;
        
        // اضافه کردن به صفحه
        if (header !== document.body) {
            header.appendChild(newCounter);
        }
    }
}

// بهبود تابع removeFromCart برای فعال‌سازی دکمه افزودن محصول
function removeFromCart(packageId) {
    console.log(`=== حذف محصول با شناسه ${packageId} از سبد خرید ===`);
    
    // نمایش حالت در حال بارگذاری
    const cartItemRow = document.querySelector(`tr[data-package-id="${packageId}"], .cart-item[data-package-id="${packageId}"]`);
    if (cartItemRow) {
        cartItemRow.classList.add('removing');
    }
    
    // نمایش حالت در حال بارگذاری در offcanvas
    const offcanvasItem = document.querySelector(`.cart-canvas [data-package-id="${packageId}"]`)?.closest('.nav-item');
    if (offcanvasItem) {
        offcanvasItem.classList.add('removing');
    }
    
    // دریافت توکن CSRF
    const csrfToken = getCookie("csrftoken");
    
    // ارسال درخواست به سرور
    const formData = new FormData();
    formData.append('package_id', packageId);
    formData.append('csrfmiddlewaretoken', csrfToken);

    // استفاده از URL صحیح براساس view موجود در Django
    fetch("/delete-cart-item/", {
        method: "POST",
        headers: {
            "X-CSRFToken": csrfToken,
            "X-Requested-With": "XMLHttpRequest"
        },
        body: formData
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`خطای HTTP ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        // به‌روزرسانی شمارنده سبد خرید
        const cartCount = data.cart_items_count || 0;
        updateHeaderCartCount(cartCount);
        
        // حذف آیتم از صفحه اصلی سبد خرید
        if (cartItemRow) {
            cartItemRow.classList.add('removed');
            setTimeout(() => {
                cartItemRow.remove();
            }, 500);
        }
        
        // حذف آیتم از offcanvas
        if (offcanvasItem) {
            offcanvasItem.classList.add('removed');
            setTimeout(() => {
                offcanvasItem.remove();
            }, 500);
        }
        
        // به‌روزرسانی قیمت‌های کل
        if (typeof updateTotalPrices === 'function') {
            updateTotalPrices(data);
        }
        
        // اگر سبد خرید خالی شد، نمایش پیام مناسب
        if (cartCount === 0) {
            if (typeof showEmptyCartMessage === 'function') {
                showEmptyCartMessage();
            }
            
            // بروزرسانی offcanvas وقتی سبد خرید خالی است
            const offcanvasBody = document.querySelector('.offcanvas-body .navbar-nav.cart-canvas-parent');
            if (offcanvasBody) {
                offcanvasBody.innerHTML = `
                    <li class="nav-item text-center p-4">
                        <div class="empty-cart">
                            <i class="bi bi-basket font-50 text-muted"></i>
                            <p class="mt-3">سبد خرید شما خالی است</p>
                        </div>
                    </li>
                `;
            }
            
            // بروزرسانی قیمت کل به صفر
            const totalPriceElement = document.querySelector('.cart-canvas-foot-sum h5');
            if (totalPriceElement) {
                totalPriceElement.textContent = '0 تومان';
            }
        }
        
        // مهم: به‌روزرسانی cartManager برای حذف آیتم
        if (window.cartManager) {
            // حذف آیتم از آرایه items
            window.cartManager.removeItem(packageId);
            
            // بررسی آیا محصول در صفحه جزئیات محصول فعلی است
            const currentProductPackageId = $("#package-id").val();
            if (currentProductPackageId === packageId) {
                // فعال‌سازی دکمه افزودن به سبد خرید
                window.cartManager.updateUI(packageId);
            }
        }
        
        // نمایش پیام موفقیت
        showAlert("✅ محصول با موفقیت از سبد خرید حذف شد", "success");
    })
    .catch(error => {
        console.error("خطا در حذف محصول:", error);
        
        // حذف حالت بارگذاری
        if (cartItemRow) {
            cartItemRow.classList.remove('removing');
        }
        if (offcanvasItem) {
            offcanvasItem.classList.remove('removing');
        }
        
        // نمایش پیام خطا
        showAlert("❌ خطا در حذف محصول از سبد خرید", "error");
        
        // راه‌حل اضطراری - حذف محلی
        if (window.cartManager) {
            window.cartManager.removeItem(packageId);
            window.cartManager.updateUI(packageId);
            showAlert("⚠️ تغییرات فقط به صورت محلی اعمال شد. لطفاً صفحه را رفرش کنید.", "warning");
        }
    });
}

function updatePrices(data) {
    const itemTotalElement = document.querySelector(`#item-total-${data.package_id}`);
    if (itemTotalElement && data.item_total_price !== undefined) {
        itemTotalElement.textContent = `${data.item_total_price.toLocaleString()} تومان`;
    }
    
    if (data.total_goods_price !== undefined) {
        document.querySelectorAll('.total-goods-price').forEach(el => {
            el.textContent = `${data.total_goods_price.toLocaleString()} تومان`;
        });
    }
    
    if (data.total_discount !== undefined) {
        document.querySelectorAll('.total-discount').forEach(el => {
            el.textContent = `${data.total_discount.toLocaleString()} تومان`;
        });
    }
    
    if (data.total_price !== undefined) {
        document.querySelectorAll('.total-price').forEach(el => {
            el.textContent = `${data.total_price.toLocaleString()} تومان`;
        });
    }
}

// تابع به‌روزرسانی قیمت‌های کل
function updateTotalPrices(data) {
    // به‌روزرسانی قیمت کل کالاها
    if (data.total_goods_price !== undefined) {
        document.querySelectorAll('.total-goods-price').forEach(el => {
            el.textContent = `${numberWithCommas(data.total_goods_price)} تومان`;
        });
    }
    
    // به‌روزرسانی مجموع تخفیف‌ها
    if (data.total_discount !== undefined) {
        document.querySelectorAll('.total-discount').forEach(el => {
            el.textContent = `${numberWithCommas(data.total_discount)} تومان`;
        });
    }
    
    // به‌روزرسانی قیمت نهایی
    if (data.total_price !== undefined) {
        document.querySelectorAll('.total-price').forEach(el => {
            el.textContent = `${numberWithCommas(data.total_price)} تومان`;
        });
    }
}

// تابع نمایش پیام سبد خرید خالی
function showEmptyCartMessage() {
    // بررسی آیا در صفحه سبد خرید هستیم یا خیر
    const isCartPage = window.location.pathname.includes('/cart') || window.location.href.includes('/cart');
    
    if (isCartPage) {
        // در صفحه سبد خرید هستیم
        const cartProductItems = document.querySelectorAll('.cart-product-item');
        const cartSummary = document.querySelector('.cart-summary');
        const discountBlocks = document.querySelectorAll('.show-discount-modal');
        const cartContainer = document.querySelector('.col-lg-9');
        
        // حذف تمام محصولات
        cartProductItems.forEach(item => {
            item.remove();
        });
        
        // مخفی کردن بخش خلاصه سبد خرید
        if (cartSummary) {
            cartSummary.style.display = 'none';
        }
        
        // مخفی کردن بخش‌های کوپن تخفیف
        discountBlocks.forEach(block => {
            block.style.display = 'none';
        });
        
        // ایجاد و نمایش پیام سبد خرید خالی
        if (cartContainer) {
            const emptyMessage = document.createElement('div');
            emptyMessage.className = 'empty-cart-message';
            emptyMessage.innerHTML = `
                <div class="text-center p-5 bg-white rounded-3 shadow-sm">
                    <i class="bi bi-basket font-60 text-muted mb-3 d-block"></i>
                    <h4 class="mb-3">سبد خرید شما خالی است</h4>
                    <p class="text-muted mb-4">می‌توانید به فروشگاه بازگشته و محصولات مورد نظر خود را اضافه کنید</p>
                    <a href="/products" class="btn main-color-one-bg border-0 px-4 py-2">مشاهده محصولات</a>
                </div>
            `;
            
            cartContainer.appendChild(emptyMessage);
        }
    } else {
        // در صفحه‌های دیگر (مانند offcanvas در هدر) هستیم
        const cartTable = document.querySelector('.cart-table');
        const cartSummary = document.querySelector('.cart-summary');
        
        if (cartTable) {
            // مخفی کردن جدول سبد خرید
            cartTable.style.display = 'none';
            
            // ایجاد و نمایش پیام سبد خرید خالی
            const emptyMessage = document.createElement('div');
            emptyMessage.className = 'empty-cart-message';
            emptyMessage.innerHTML = `
                <div class="text-center p-5">
                    <i class="fas fa-shopping-cart fa-4x text-muted mb-3"></i>
                    <h4>سبد خرید شما خالی است</h4>
                    <p>می‌توانید به فروشگاه بازگشته و محصولات مورد نظر خود را اضافه کنید</p>
                    <a href="/shop/" class="btn btn-primary mt-3">مشاهده محصولات</a>
                </div>
            `;
            
            cartTable.parentNode.insertBefore(emptyMessage, cartTable);
        }
        
        // مخفی کردن خلاصه سبد خرید
        if (cartSummary) {
            cartSummary.style.display = 'none';
        }
        
        // بروزرسانی offcanvas وقتی سبد خرید خالی است
        const offcanvasBody = document.querySelector('.offcanvas-body .navbar-nav.cart-canvas-parent');
        if (offcanvasBody) {
            offcanvasBody.innerHTML = `
                <li class="nav-item text-center p-4">
                    <div class="empty-cart">
                        <i class="bi bi-basket font-50 text-muted"></i>
                        <p class="mt-3">سبد خرید شما خالی است</p>
                    </div>
                </li>
            `;
        }
    }
}

// افزودن یک تابع کمکی برای بررسی صفحه فعلی
function isProductDetailPage() {
    // بررسی وجود المان‌های خاص صفحه جزئیات محصول
    return $("#add-to-cart-form").length > 0 && $("#package-id").length > 0;
}

// یک تابع جدید برای بررسی و به‌روزرسانی دکمه در صفحه جزئیات محصول
function checkAndUpdateAddButton() {
    if (isProductDetailPage()) {
        const currentPackageId = $("#package-id").val();
        if (currentPackageId) {
            window.cartManager.updateUI(currentPackageId);
        }
    }
}
