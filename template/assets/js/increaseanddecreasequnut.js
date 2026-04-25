document.addEventListener("DOMContentLoaded", function () {
    const decreaseButtons = document.querySelectorAll(".decrease-btn");
    const increaseButtons = document.querySelectorAll(".increase-btn");
    const counterInputs = document.querySelectorAll(".counter-input");

    // رویداد کلیک برای دکمه کاهش
    decreaseButtons.forEach((button) => {
        button.addEventListener("click", function (e) {
            // Prevent default behavior
            e.preventDefault();
            const inputField = button.parentElement.querySelector(".counter-input");
            const currentValue = parseInt(inputField.value) || 0; // مقدار فعلی با بررسی معتبر بودن
            if (currentValue > 1) {
                // Update the input value immediately to improve UI responsiveness
                inputField.value = currentValue - 1;
                updateCart(inputField, currentValue - 1);
            } else {
                console.log("مقدار نمی‌تواند کمتر از 1 باشد.");
            }
        });
    });

    // رویداد کلیک برای دکمه افزایش
    increaseButtons.forEach((button) => {
        button.addEventListener("click", function (e) {
            // Prevent default behavior
            e.preventDefault();
            const inputField = button.parentElement.querySelector(".counter-input");
            const maxQuantity = parseInt(button.dataset.maxQuantity) || Infinity; // مقدار حداکثر
            const currentValue = parseInt(inputField.value) || 0;
            if (currentValue < maxQuantity) {
                // Update the input value immediately to improve UI responsiveness
                inputField.value = currentValue + 1;
                updateCart(inputField, currentValue + 1);
            } else {
                alert("موجودی کافی نیست!");
            }
        });
    });

    // رویداد تغییر برای فیلد ورودی
    counterInputs.forEach((input) => {
        input.addEventListener("change", function() {
            const maxQuantity = parseInt(input.closest('.counter').querySelector('.increase-btn').dataset.maxQuantity) || 100;
            const minQuantity = 1;
            let value = parseInt(input.value) || minQuantity;
            
            // محدود کردن مقدار به حداقل و حداکثر مجاز
            value = Math.max(minQuantity, Math.min(value, maxQuantity));
            
            // تنظیم مقدار در فیلد ورودی
            input.value = value;
            
            // به‌روزرسانی سبد خرید
            updateCart(input, value);
        });
        
        // غیرفعال کردن ورودی مستقیم با کلیک
        input.addEventListener("focus", function() {
            this.blur();
        });
    });

    // تابع به‌روزرسانی سبد خرید
    function updateCart(inputField, newCount) {
        const packageId = inputField.dataset.packageId;

        if (!packageId) {
            console.error("packageId مشخص نشده است.");
            return;
        }

        // اضافه کردن کلاس loading به المان پدر برای نمایش وضعیت در حال بارگذاری
        const counterElement = inputField.closest('.counter');
        if (counterElement) {
            counterElement.classList.add('updating');
            counterElement.classList.add('loading');
        }

        fetch("/update-cart-item/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCookie("csrftoken")
            },
            body: JSON.stringify({
                package_id: packageId,
                count: newCount
            })
        })
        .then((response) => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then((data) => {
            // حذف کلاس loading
            if (counterElement) {
                counterElement.classList.remove('loading');
                counterElement.classList.remove('updating');
                // اضافه کردن کلاس updated برای نمایش انیمیشن به‌روزرسانی
                counterElement.classList.add('updated');
                setTimeout(() => {
                    counterElement.classList.remove('updated');
                }, 1000);
            }
            
            if (data.status === "success") {
                console.log("موفقیت:", data);
                
                // بروزرسانی تمام المان‌های counter-input با همان package_id
                document.querySelectorAll(`.counter-input[data-package-id="${packageId}"]`).forEach(input => {
                    input.value = newCount;
                    // اضافه کردن کلاس به‌روزرسانی برای انیمیشن
                    input.classList.add('updated-count');
                    setTimeout(() => {
                        input.classList.remove('updated-count');
                    }, 1000);
                });

                // به‌روزرسانی مقادیر دیگر (اگر وجود دارد)
                const itemTotal = document.querySelector(`#item-total-${packageId}`);
                const totalGoodsPrice = document.querySelector("#total-goods-price");
                const totalDiscount = document.querySelector("#total-discount");
                const totalPrice = document.querySelector("#total-price");

                if (itemTotal) {
                    itemTotal.textContent = `${data.item_total_price.toLocaleString()}تومان `;
                }
                if (totalGoodsPrice) {
                    totalGoodsPrice.textContent = `${data.total_goods_price.toLocaleString()} `;
                }
                if (totalDiscount) {
                    totalDiscount.textContent = `${data.total_discount.toLocaleString()} تومان `;
                }
                if (totalPrice) {
                    totalPrice.textContent = `${data.total_price.toLocaleString()} تومان `;
                }
                
                // بروزرسانی شمارنده سبد خرید
                updateCartCounter(data.cart_items_count || 0);
                
                // این خط مهم است - بروزرسانی کامل offcanvas سبد خرید
                loadCartOffcanvas();
            } else {
                console.error("خطا در به‌روزرسانی:", data.message);
            }
        })
        .catch((error) => {
            // حذف کلاس loading در صورت خطا
            if (counterElement) {
                counterElement.classList.remove('loading');
                counterElement.classList.remove('updating');
            }
            
            // در صورت خطا، برگرداندن مقدار قبلی
            const oldValue = newCount > 1 ? newCount + 1 : 1; // اگر کم شده بود برگردان به مقدار قبلی
            inputField.value = newCount < 1 ? 1 : oldValue;
            
            console.error("خطا در AJAX:", error);
            
            // نمایش پیام خطا به کاربر
            if (typeof showAlert === 'function') {
                showAlert("خطا در به‌روزرسانی سبد خرید", "error");
            } else {
                alert("خطا در به‌روزرسانی سبد خرید. لطفاً دوباره تلاش کنید.");
            }
        });
    }

    // تابع دریافت کوکی CSRF
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== "") {
            const cookies = document.cookie.split(";");
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === `${name}=`) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    
    // تابع جدید برای بروزرسانی شمارنده سبد خرید
    function updateCartCounter(count) {
        const counterElements = document.querySelectorAll("#cartCounter, .cart-counter");
        counterElements.forEach(counter => {
            counter.textContent = count;
            
            // اضافه کردن کلاس برای نمایش انیمیشن
            counter.classList.add('counter-updated');
            setTimeout(() => {
                counter.classList.remove('counter-updated');
            }, 1000);
        });
    }
    
    // تابع جدید برای بارگذاری سبد خرید offcanvas
    function loadCartOffcanvas() {
        // بارگذاری محتوای سبد خرید از سرور
        fetch('/get-cart-content/')
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    updateOffcanvasCartContent(data);
                } else {
                    console.error('خطا در دریافت اطلاعات سبد خرید:', data.message);
                }
            })
            .catch(error => {
                console.error('خطا در دریافت اطلاعات سبد خرید:', error);
            });
    }
    
    // تابع بروزرسانی محتوای offcanvas سبد خرید
    function updateOffcanvasCartContent(data) {
        // یافتن کانتینر سبد خرید
        const cartContainer = document.querySelector('#offcanvasCart .offcanvas-body .cart-canvas-parent');
                    if (!cartContainer) {
            console.error('کانتینر سبد خرید در offcanvas یافت نشد');
                        return;
                    }
                    
        // بروزرسانی تعداد آیتم‌ها در عنوان سبد خرید
                    const cartTitle = document.querySelector('#offcanvasCartLabel');
                    if (cartTitle && data.cart_items) {
            cartTitle.innerHTML = `سبد خرید <small class="text-muted ms-1">(${data.cart_items.length} مورد)</small>`;
                    }
                    
        // اگر سبد خرید خالی باشد
                    if (!data.cart_items || data.cart_items.length === 0) {
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
                    
        // ساخت HTML برای آیتم‌های سبد خرید
                    let cartHTML = '';
                    let totalPrice = 0;
                    
                    data.cart_items.forEach(item => {
            // محاسبه قیمت کل آیتم
            const itemTotalPrice = item.price * item.count;
            totalPrice += itemTotalPrice;
                        
                        cartHTML += `
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
                                        <h6 class="title-font main-color-one-color">${numberWithCommas(item.price)} تومان</h6>
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
                    });
                    
        // بروزرسانی HTML سبد خرید
                    cartContainer.innerHTML = cartHTML;
                    
        // بروزرسانی قیمت کل
                    const totalPriceElement = document.querySelector('.cart-canvas-foot-sum h5');
                    if (totalPriceElement) {
                        totalPriceElement.textContent = `${numberWithCommas(totalPrice)} تومان`;
                    }
                    
        // اضافه کردن رویداد کلیک به دکمه‌های حذف
        document.querySelectorAll('.delete-cart-item').forEach(button => {
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

    // تابع حذف آیتم از سبد خرید - باید در فایل دیگر تعریف شده باشد
    // اگر تعریف نشده، باید آن را اینجا تعریف کنید
    if (typeof removeFromCart !== 'function') {
        window.removeFromCart = function(packageId) {
            if (!packageId) {
                console.error("شناسه پکیج نامعتبر");
                return;
            }
            
            fetch("/delete-cart-item/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCookie("csrftoken")
                },
                body: JSON.stringify({ package_id: packageId })
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === "success") {
                    console.log("محصول با موفقیت حذف شد");
                    
                    // بروزرسانی شمارنده سبد خرید
                    updateCartCounter(data.cart_items_count || 0);
                    
                    // بروزرسانی offcanvas
                    loadCartOffcanvas();
                    
                    // اگر در صفحه سبد خرید هستیم، ردیف محصول را حذف کنیم
                    const cartRow = document.querySelector(`tr[data-package-id="${packageId}"]`);
                    if (cartRow) {
                        cartRow.remove();
                    }
                } else {
                    console.error("خطا در حذف محصول:", data.message);
                }
            })
            .catch(error => {
                console.error("خطا در AJAX:", error);
            });
        };
    }
    
    // فراخوانی اولیه برای بارگذاری سبد خرید در offcanvas
    // این را می‌توانید حذف کنید اگر offcanvas به صورت خودکار بارگذاری می‌شود
    document.querySelectorAll('[data-bs-toggle="offcanvas"][href="#offcanvasCart"]').forEach(button => {
        button.addEventListener('click', function() {
            loadCartOffcanvas();
        });
    });
    
    // همچنین استایل‌های مورد نیاز را اضافه کنیم
    const style = document.createElement('style');
    style.innerHTML = `
        .counter.loading {
            opacity: 0.7;
            pointer-events: none;
        }
        
        .counter-updated {
            animation: pulse 1s ease;
        }
        
        .highlight-change {
            animation: highlight 1.5s ease;
        }
        
        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.2); color: #ff6b6b; }
            100% { transform: scale(1); }
        }
        
        @keyframes highlight {
            0% { background-color: transparent; }
            30% { background-color: rgba(255, 193, 7, 0.2); }
            100% { background-color: transparent; }
        }
    `;
    document.head.appendChild(style);
});
