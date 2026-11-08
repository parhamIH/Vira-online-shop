
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""ساخت داده‌های نمایشی برای فروشگاه Vira."""

from __future__ import annotations

import argparse
import html
import os
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError


# ============================================================
# DJANGO SETUP
# ============================================================

def setup_django():
    import django

    candidates = [
        os.environ.get("DJANGO_SETTINGS_MODULE"),
        "main.settings",
        "main.config.settings",
        "config.settings",
    ]

    last_error = None

    for module in dict.fromkeys(x for x in candidates if x):
        try:
            os.environ["DJANGO_SETTINGS_MODULE"] = module
            django.setup()
            print(f"[Django] settings: {module}")
            return
        except Exception as exc:
            last_error = exc

    raise RuntimeError(f"Django setup failed: {last_error!r}")


def get_model(app, name, required=True):
    from django.apps import apps

    try:
        return apps.get_model(app, name)
    except LookupError:
        if required:
            raise RuntimeError(f"Model {app}.{name} not found")
        return None


# ============================================================
# DEMO DATA
# ============================================================

CATEGORIES = [
    ("دیجیتال و لوازم جانبی", "digital-accessories"),
    ("پوشاک مردانه", "menswear"),
    ("پوشاک زنانه", "womenswear"),
    ("کیف و کفش", "bags-and-shoes"),
    ("خانه و سبک زندگی", "home-lifestyle"),
    ("زیبایی و سلامت", "beauty-care"),
]

# name, category, sale price, regular price, stock

PRODUCTS = [
    ("هدفون بی‌سیم نویزکنسلینگ", "digital-accessories", 3490000, 4200000, 24),
    ("ساعت هوشمند اسپرت", "digital-accessories", 5890000, 6500000, 18),
    ("پاوربانک ۲۰۰۰۰ میلی‌آمپر", "digital-accessories", 1790000, 2100000, 42),
    ("اسپیکر بلوتوث قابل حمل", "digital-accessories", 2250000, 2700000, 31),
    ("دوربین دیجیتال کامپکت", "digital-accessories", 18900000, 21000000, 7),
    ("ماوس بی‌سیم ارگونومیک", "digital-accessories", 890000, 1050000, 55),
    ("کیبورد مکانیکی", "digital-accessories", 3150000, 3600000, 16),
    ("شارژر سریع USB-C", "digital-accessories", 690000, 850000, 63),
    ("عینک آفتابی کلاسیک", "bags-and-shoes", 1250000, 1500000, 29),
    ("کوله‌پشتی روزمره", "bags-and-shoes", 2450000, 2900000, 14),
    ("کتانی روزمره سفید", "bags-and-shoes", 3850000, 4400000, 21),
    ("کفش پیاده‌روی", "bags-and-shoes", 4290000, 4900000, 12),
    ("تی‌شرت ساده پنبه‌ای", "menswear", 590000, 750000, 80),
    ("هودی دورس مینیمال", "menswear", 1890000, 2200000, 26),
    ("پیراهن آستین‌بلند", "menswear", 1350000, 1600000, 19),
    ("شلوار جین راسته", "menswear", 1990000, 2300000, 22),
    ("مانتو روزمره", "womenswear", 2750000, 3200000, 15),
    ("شومیز لینن", "womenswear", 1450000, 1750000, 23),
    ("کیف دستی مینیمال", "womenswear", 2190000, 2600000, 11),
    ("شال نخی چهارفصل", "womenswear", 490000, 620000, 47),
    ("چراغ مطالعه رومیزی", "home-lifestyle", 1150000, 1400000, 17),
    ("ماگ سرامیکی", "home-lifestyle", 320000, 420000, 65),
    ("بطری آب استیل", "home-lifestyle", 780000, 950000, 34),
    ("کوسن دکوراتیو", "home-lifestyle", 560000, 690000, 38),
    ("عطر روزانه مردانه", "beauty-care", 2650000, 3100000, 9),
    ("عطر ملایم زنانه", "beauty-care", 2890000, 3300000, 13),
    ("کرم مرطوب‌کننده", "beauty-care", 420000, 520000, 44),
    ("ست مراقبت پوست", "beauty-care", 1750000, 2050000, 20),
    ("کیف پول چرمی", "bags-and-shoes", 1090000, 1300000, 27),
    ("هدفون روگوشی استودیویی", "digital-accessories", 4750000, 5400000, 8),
]


PHOTO_IDS = [
    "photo-1505740420928-5e560c06d30e",
    "photo-1523275335684-37898b6baf30",
    "photo-1542291026-7eec264c27ff",
    "photo-1526170375885-4d8ecf77b99f",
    "photo-1553062407-98eeb64c6a62",
    "photo-1585386959984-a4155224a1ad",
    "photo-1521572163474-6864f9cf17ab",
    "photo-1503602642458-232111445657",
    "photo-1512499617640-c74ae3a79d37",
]

IMAGE_CACHE = {}
PLACEHOLDERS_ONLY = False


# ============================================================
# IMAGES
# ============================================================

def make_placeholder(title, index):
    from PIL import Image, ImageDraw
    from io import BytesIO

    colors = [
        "#e8edf5",
        "#f2e9e2",
        "#e5eee9",
        "#f1e9ef",
        "#e9eef0",
    ]

    bg = colors[index % len(colors)]

    image = Image.new("RGB", (1000, 1000), bg)
    draw = ImageDraw.Draw(image)

    # شکل مرکزی
    draw.rounded_rectangle(
        (250, 220, 750, 680),
        radius=60,
        fill="#ffffff",
        outline="#cbd5e1",
        width=5,
    )

    draw.ellipse(
        (390, 280, 610, 500),
        fill="#64748b",
    )

    # متن انگلیسی برای سازگاری با فونت پیش‌فرض
    draw.text(
        (405, 550),
        "VIRA DEMO",
        fill="#273449",
    )

    buffer = BytesIO()

    image.save(
        buffer,
        format="PNG",
        optimize=True,
    )

    return buffer.getvalue()


def get_photo(index, title):
    key = index % len(PHOTO_IDS)

    if key in IMAGE_CACHE:
        return IMAGE_CACHE[key]

    if not PLACEHOLDERS_ONLY:

        url = (
            f"https://images.unsplash.com/{PHOTO_IDS[key]}"
            "?auto=format&fit=crop&w=1000&q=82"
        )

        try:
            request = Request(
                url,
                headers={"User-Agent": "ViraDemoSeeder/1.0"},
            )

            with urlopen(request, timeout=12) as response:
                data = response.read()
                content_type = response.headers.get(
                    "Content-Type", ""
                )

                if (
                    response.status == 200
                    and content_type.startswith("image/")
                    and len(data) > 3000
                ):
                    ext = ".png" if "png" in content_type else ".jpg"
                    IMAGE_CACHE[key] = (data, ext)
                    return IMAGE_CACHE[key]

        except (URLError, HTTPError, TimeoutError, OSError):
            pass

    IMAGE_CACHE[key] = (
        make_placeholder(title, index),
        ".png"
    )
    return IMAGE_CACHE[key]


def save_image(
    instance,
    field_name,
    index,
    title,
    filename,
    refresh=False,
):
    from django.core.files.base import ContentFile

    field_file = getattr(instance, field_name)

    if field_file and field_file.name and not refresh:
        return False

    data, ext = get_photo(index, title)

    field_file.save(
        f"{filename}{ext}",
        ContentFile(data),
        save=False,
    )

    instance.save(update_fields=[field_name])

    return True


# ============================================================
# CHOICE HELPER
# ============================================================

def choice(model, field_name, preferred, fallback):
    try:
        field = model._meta.get_field(field_name)
        choices = list(field.choices or [])
    except Exception:
        return fallback

    if not choices:
        return fallback

    wanted = [str(x).lower() for x in preferred]

    for value, label in choices:
        text = f"{value} {label}".lower()

        if any(word in text for word in wanted):
            return value

    return choices[0][0]


# ============================================================
# USERS
# ============================================================

def create_users(User, Profile):
    users = []

    for i in range(1, 5):
        username = f"vira_demo_{i:02d}"
        email = f"customer{i:02d}@vira-demo.local"

        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                "email": email,
                "first_name": f"مشتری {i}",
                "last_name": "دمو",
                "is_active": True,
                "is_staff": False,
                "is_superuser": False,
            },
        )

        if created:
            user.set_password("ViraDemo@2026")
            user.save(update_fields=["password"])
            print(f"[NEW] User: {username}")
        else:
            print(f"[EXISTS] User: {username}")

        profile, profile_created = Profile.objects.get_or_create(
            user=user,
            defaults={
                "phone_number": f"0912111{i:04d}",
                "is_phone_verified": True,
                "job": "کاربر آزمایشی",
            },
        )

        if profile_created:
            print(f"[NEW] Profile: {username}")

        users.append(user)

    return users


# ============================================================
# CATEGORIES
# ============================================================


def create_categories(
    BaseCategories,
    Category,
    refresh_images,
):
    bases = {}
    categories = {}

    # نام کوتاه دسته‌ها برای رعایت محدودیت دیتابیس
    short_names = {
        "digital-accessories": "دیجیتال",
        "menswear": "مردانه",
        "womenswear": "زنانه",
        "bags-and-shoes": "کیف و کفش",
        "home-lifestyle": "خانه",
        "beauty-care": "زیبایی",
    }

    for index, (name, slug) in enumerate(CATEGORIES):

        # --------------------------------
        # ساخت دسته مادر
        # --------------------------------

        base, base_created = BaseCategories.objects.get_or_create(
            name=name,
            defaults={
                "en_name": slug,
                "description": f"دسته اصلی {name} در فروشگاه ویرا.",
            },
        )

        save_image(
            base,
            "image",
            index,
            name,
            f"base-category-{slug}",
            refresh_images,
        )

        if base_created:
            print(f"[NEW] Base Category: {name}")
        else:
            print(f"[EXISTS] Base Category: {name}")

        bases[slug] = base

        # --------------------------------
        # تعیین نام دسته فرعی
        # --------------------------------

        category_name = short_names.get(slug, name)

        # بررسی محدودیت طول فیلد name
        max_length = Category._meta.get_field("name").max_length

        if max_length and len(category_name) > max_length:
            category_name = category_name[:max_length]

        # بررسی محدودیت طول en_name
        en_max_length = Category._meta.get_field("en_name").max_length

        category_slug = slug

        if en_max_length:
            category_slug = category_slug[:en_max_length]

        # --------------------------------
        # ساخت دسته فرعی
        # --------------------------------

        category, cat_created = Category.objects.get_or_create(
            name=category_name,
            defaults={
                "en_name": category_slug,
                "description": (
                    f"محصولات گروه {name} در فروشگاه ویرا."
                ),
                "base_catgory": base,
            },
        )

        # ترمیم رابطه دسته مادر
        if category.base_catgory_id != base.pk:
            category.base_catgory = base
            category.save(update_fields=["base_catgory"])

        # --------------------------------
        # ثبت تصویر دسته
        # --------------------------------

        save_image(
            category,
            "image",
            index + 2,
            category_name,
            f"category-{slug}",
            refresh_images,
        )

        if cat_created:
            print(f"[NEW] Category: {category_name}")
        else:
            print(f"[EXISTS] Category: {category_name}")

        categories[slug] = category

    return bases, categories

# ============================================================
# BRAND
# ============================================================

def create_brand(Brand, categories, bases):

    brand, created = Brand.objects.get_or_create(
        name="ویرا",
        defaults={
            "en_name": "vira-demo",
        },
    )

    category_field = next(
        (
            f for f in Brand._meta.many_to_many
            if f.remote_field.model.__name__ == "Category"
        ),
        None,
    )

    if category_field:
        getattr(brand, category_field.name).add(
            *categories.values()
        )

    for base in bases.values():

        brand_field = next(
            (
                f for f in base._meta.many_to_many
                if f.remote_field.model == Brand
            ),
            None,
        )

        if brand_field:
            getattr(base, brand_field.name).add(brand)

    print(f"[{'NEW' if created else 'EXISTS'}] Brand: ویرا")

    return brand


# ============================================================
# WARRANTY
# ============================================================

def create_warranty(Warranty):

    warranty, created = Warranty.objects.get_or_create(
        name="گارانتی دمو ویرا",
        defaults={
            "company": "خدمات نمونه ویرا",
            "duration": 12,
            "is_active": True,
            "description": "گارانتی آزمایشی ۱۲ ماهه.",
            "terms_conditions": "این گارانتی صرفاً برای داده‌های دمو است.",
            "support_phone": "02100000000",
            "registration_required": False,
        },
    )

    print(f"[{'NEW' if created else 'EXISTS'}] Warranty")

    return warranty


# ============================================================
# PRODUCTS
# ============================================================

def create_products(
    Product,
    categories,
    limit,
    refresh_images,
):

    products = []
    data_map = {}

    for index, (name, slug, sale, regular, stock) in enumerate(
        PRODUCTS[:limit]
    ):

        product, created = Product.objects.get_or_create(
            name=name,
            defaults={
                "description": (
                    f"{name} با طراحی کاربردی و کیفیت مناسب. "
                    "این محصول برای نمایش امکانات فروشگاه ویرا "
                    "در محیط دمو ثبت شده است."
                ),
                "is_active": True,
            },
        )

        save_image(
            product,
            "image",
            index,
            name,
            f"product-{index + 1:03d}",
            refresh_images,
        )

        category = categories[slug]
        product.categories.add(category)

        print(f"[{'NEW' if created else 'EXISTS'}] Product: {name}")

        products.append(product)

        data_map[product.pk] = {
            "sale": sale,
            "regular": regular,
            "stock": stock,
            "index": index,
            "name": name,
        }

    return products, data_map


# ============================================================
# PRODUCT PACKAGES
# ============================================================

def create_packages(
    products,
    data_map,
    ProductPackage,
    warranty,
    brand,
):

    packages = {}

    for product in products:

        data = data_map[product.pk]

        discount = round(
            (data["regular"] - data["sale"])
            * 100
            / data["regular"]
        )

        package, created = ProductPackage.objects.get_or_create(
            product=product,
            waranty=warranty,
            defaults={
                "brand": brand,
                "price": data["regular"],
                "final_price": data["sale"],
                "quantity": data["stock"],
                "is_active_package": True,
                "discount": discount,
                "is_active_discount": discount > 0,
                "sold_count": 0,
                "views_count": 10 + data["index"] * 3,
                "rating": 4.2 + (data["index"] % 8) / 10,
                "attributs": {
                    "demo": True,
                    "demo_code": f"VIRA-PKG-{data['index'] + 1:04d}",
                },
            },
        )

        # به‌روزرسانی بسته‌های دمو قبلی
        package.price = data["regular"]
        package.final_price = data["sale"]
        package.quantity = data["stock"]
        package.is_active_package = True
        package.discount = discount
        package.is_active_discount = discount > 0

        if brand:
            package.brand = brand

        package.save()

        packages[product.pk] = package

        print(
            f"[{'NEW' if created else 'EXISTS/UPDATED'}] "
            f"Package: {product.name}"
        )

    return packages


# ============================================================
# PRODUCT GALLERY
# ============================================================

def create_gallery(products, Gallery):

    added = 0

    for index, product in enumerate(products):

        target_count = 2 if index < 12 else 1

        existing = Gallery.objects.filter(
            product=product
        ).count()

        while existing < target_count:

            gallery = Gallery(product=product)

            photo_index = index + existing + 3

            data, ext = get_photo(
                photo_index,
                product.name,
            )

            from django.core.files.base import ContentFile

            gallery.image.save(
                f"gallery-{product.pk}-{existing + 1}{ext}",
                ContentFile(data),
                save=False,
            )

            gallery.save()

            existing += 1
            added += 1

    return added


# ============================================================
# ADDRESS
# ============================================================

def create_addresses(users, ClientAddress):

    addresses = []

    for index, user in enumerate(users, 1):

        address, created = ClientAddress.objects.get_or_create(
            user=user,
            title_address="آدرس دمو ویرا",
            defaults={
                "province": "تهران",
                "city": "تهران",
                "full_address": (
                    f"تهران، خیابان نمونه، کوچه دمو، "
                    f"پلاک {index + 10}، واحد {index}"
                ),
                "postcode": f"12345678{index:02d}",
            },
        )

        if created:
            print(f"[NEW] Address: {user.username}")

        addresses.append(address)

    return addresses


# ============================================================
# CARTS
# ============================================================

def create_carts(users, Cart):

    carts = []

    for index, user in enumerate(users, 1):

        cart_number = f"VIRA-DEMO-CART-{index:04d}"

        cart = Cart.objects.filter(
            cart_number=cart_number
        ).first()

        if cart is None:
            cart = Cart.objects.filter(
                user=user,
                is_paid=False,
            ).order_by("-created_date").first()

        if cart is None:

            cart = Cart.objects.create(
                user=user,
                cart_number=cart_number,
                status=choice(
                    Cart,
                    "status",
                    ["pending", "open", "active"],
                    "pending",
                ),
                is_paid=False,
            )

            print(f"[NEW] Cart: {cart.cart_number}")

        else:
            print(f"[EXISTS] Cart: {cart.cart_number}")

        carts.append(cart)

    return carts


# ============================================================
# CART ITEMS
# ============================================================

def create_cart_items(
    carts,
    products,
    packages,
    CartItem,
):

    added = 0

    for index, cart in enumerate(carts):

        for line in range(2):

            product = products[
                (index * 3 + line) % len(products)
            ]

            package = packages.get(product.pk)

            if package is None:
                continue

            item, created = CartItem.objects.get_or_create(
                cart=cart,
                package=package,
                defaults={
                    "count": line + 1,
                    "final_price": package.final_price,
                },
            )

            if created:
                added += 1

                print(
                    f"[NEW] Cart Item: "
                    f"{cart.cart_number} / {product.name}"
                )

    return added


# ============================================================
# ORDERS
# ============================================================


def create_orders(
    carts,
    users,
    addresses,
    Order,
    CartItem,
):
    added = 0

    desired_statuses = [
        "delivered",
        "processing",
        "pending",
        "cancelled",
    ]

    for index, (cart, user, address) in enumerate(
        zip(carts, users, addresses)
    ):

        # بررسی سفارش قبلی
        existing_order = Order.objects.filter(
            cart=cart
        ).first()

        if existing_order:

            print(
                f"[EXISTS] Order: "
                f"{existing_order.order_number}"
            )

            # ترمیم وضعیت سبد اولین سفارش دمو
            if index == 0:
                cart.__class__.objects.filter(
                    pk=cart.pk
                ).update(is_paid=True)

                cart.is_paid = True

            continue

        # دریافت آیتم‌های سبد خرید
        items = list(
            CartItem.objects.filter(cart=cart)
            .select_related("package")
        )

        if not items:
            print(
                f"[SKIP] Order {index + 1}: cart is empty"
            )
            continue

        # محاسبه مبلغ سفارش
        total = sum(
            int(
                item.final_price
                if item.final_price is not None
                else item.package.final_price
            ) * int(item.count)
            for item in items
        )

        desired_status = desired_statuses[
            index % len(desired_statuses)
        ]

        # ساخت سفارش
        order = Order.objects.create(
            user=user,
            cart=cart,
            address=address,

            order_number=(
                f"VIRA-DEMO-ORDER-{index + 1:04d}"
            ),

            payment_method=choice(
                Order,
                "payment_method",
                ["online", "card", "gateway"],
                "online",
            ),

            payment_status=choice(
                Order,
                "payment_status",
                (
                    ["paid", "success"]
                    if index == 0
                    else ["pending", "waiting"]
                ),
                "paid" if index == 0 else "pending",
            ),

            status=choice(
                Order,
                "status",
                [desired_status],
                desired_status,
            ),

            total_price=total,
            shipping_cost=0,
            discount_amount=0,

            notes=(
                "این سفارش برای نمایش امکانات "
                "فروشگاه ویرا ساخته شده است."
            ),
        )

        print(
            f"[NEW] Order: {order.order_number}"
        )

        # بسیار مهم:
        # از cart.save() استفاده نمی‌کنیم؛
        # چون save سفارشی Cart به item.price دسترسی دارد.
        if index == 0:

            cart.__class__.objects.filter(
                pk=cart.pk
            ).update(is_paid=True)

            cart.is_paid = True

        added += 1

    return added

# ============================================================
# FAVORITES
# ============================================================

def create_favourites(
    users,
    products,
    FavouriteProducts,
):

    added = 0

    for index, user in enumerate(users):

        favourite, created = FavouriteProducts.objects.get_or_create(
            user=user
        )

        added += int(created)

        selected = [
            products[(index * 4 + j + 2) % len(products)]
            for j in range(3)
        ]

        favourite.products.add(*selected)

    return added


# ============================================================
# REVIEWS
# ============================================================

def create_reviews(users, products, Comment):

    added = 0

    for index in range(min(12, len(products))):

        user = users[index % len(users)]
        product = products[index]

        _obj, created = Comment.objects.get_or_create(
            user=user,
            product=product,
            defaults={
                "text": (
                    "کیفیت محصول مناسب بود و تجربه خرید خوبی داشتم. "
                    "ارسال هم رضایت‌بخش بود."
                ),
                "rating": 4 + (index % 2),
                "status": "approved",
            },
        )

        added += int(created)

    return added


# ============================================================
# ARTICLES
# ============================================================

def create_articles(Article, refresh_images):

    rows = [
        (
            "راهنمای انتخاب هدفون بی‌سیم",
            "wireless-headphone-buying-guide",
            "برای انتخاب هدفون مناسب، به کیفیت صدا، عمر باتری، "
            "راحتی و قابلیت حذف نویز توجه کنید.",
        ),
        (
            "چطور از ساعت هوشمند بهتر استفاده کنیم؟",
            "smartwatch-usage-tips",
            "با تنظیم اعلان‌ها، پایش فعالیت و مدیریت شارژ "
            "می‌توانید استفاده بهتری از ساعت هوشمند داشته باشید.",
        ),
        (
            "راهنمای نگهداری از محصولات چرمی",
            "leather-product-care",
            "محصولات چرمی را از رطوبت شدید و نور مستقیم دور نگه دارید.",
        ),
    ]

    added = 0

    for index, (title, slug, content) in enumerate(rows):

        article, created = Article.objects.get_or_create(
            slug=slug,
            defaults={
                "title": title,
                "content": content,
                "short_description": content,
                "is_published": True,
                "meta_title": title,
                "meta_description": content,
                "meta_keywords": "ویرا، راهنمای خرید، فروشگاه اینترنتی",
            },
        )

        save_image(
            article,
            "image",
            index + 4,
            title,
            f"article-{slug}",
            refresh_images,
        )

        added += int(created)

    return added


# ============================================================
# HOME SLIDER AND BANNERS
# ============================================================

def create_home_content(
    HomeSlider,
    PromotionalBanner,
    refresh_images,
):

    sliders_added = 0
    banners_added = 0

    sliders = [
        (
            "تجربه خرید هوشمند با ویرا",
            "محصولات منتخب، قیمت مناسب و خرید آسان",
            "/products/",
        ),
        (
            "تازه‌های دنیای دیجیتال",
            "ابزارهای کاربردی برای زندگی روزمره",
            "/products/",
        ),
    ]

    for index, (title, subtitle, link) in enumerate(sliders):

        slider, created = HomeSlider.objects.get_or_create(
            title=title,
            defaults={
                "subtitle": subtitle,
                "link": link,
                "active": True,
                "order": index + 1,
            },
        )

        save_image(
            slider,
            "image",
            index + 10,
            title,
            f"home-slider-{index + 1}",
            refresh_images,
        )

        sliders_added += int(created)

    banners = [
        ("پیشنهادهای ویژه دیجیتال", "/products/"),
        ("استایل روزمره با ویرا", "/products/"),
    ]

    for index, (title, link) in enumerate(banners):

        banner, created = PromotionalBanner.objects.get_or_create(
            title=title,
            defaults={
                "link": link,
                "active": True,
                "order": index + 1,
            },
        )

        save_image(
            banner,
            "image",
            index + 12,
            title,
            f"promo-banner-{index + 1}",
            refresh_images,
        )

        banners_added += int(created)

    return sliders_added, banners_added


# ============================================================
# STATIC PAGES
# ============================================================

def create_static_pages(StaticPage):

    pages = [
        (
            "درباره ویرا",
            "about-vira",
            "ویرا یک فروشگاه اینترنتی نمونه برای تجربه خرید ساده و مطمئن است.",
        ),
        (
            "راهنمای خرید",
            "shopping-guide",
            "محصول موردنظر را انتخاب کنید، آن را به سبد خرید بیفزایید "
            "و مراحل ثبت سفارش را تکمیل کنید.",
        ),
        (
            "شرایط ارسال و بازگشت",
            "shipping-and-returns",
            "اطلاعات ارسال و بازگشت کالا در این صفحه نمایش داده می‌شود.",
        ),
    ]

    added = 0

    for title, slug, content in pages:

        _obj, created = StaticPage.objects.get_or_create(
            slug=slug,
            defaults={
                "title": title,
                "content": content,
                "active": True,
                "seo_title": title,
                "seo_description": content,
            },
        )

        added += int(created)

    return added


# ============================================================
# NOTIFICATIONS
# ============================================================

def create_notifications(users, Notification):

    added = 0

    for user in users:

        _obj, created = Notification.objects.get_or_create(
            user=user,
            title="به ویرا خوش آمدید",
            defaults={
                "message": (
                    "حساب کاربری دمو شما با موفقیت آماده استفاده است."
                ),
                "notification_type": choice(
                    Notification,
                    "notification_type",
                    ["info", "system", "welcome"],
                    "info",
                ),
                "is_read": False,
                "related_url": "/profile",
            },
        )

        added += int(created)

    return added


# ============================================================
# SUPPORT TICKETS
# ============================================================

def create_support(
    users,
    SupportTicket,
    TicketReply,
    User,
):

    staff, created = User.objects.get_or_create(
        username="vira_demo_support",
        defaults={
            "email": "support@vira-demo.local",
            "first_name": "پشتیبانی",
            "last_name": "ویرا",
            "is_staff": True,
            "is_active": True,
        },
    )

    if created:
        staff.set_password("ViraDemo@2026")
        staff.save(update_fields=["password"])

    topics = [
        (
            "پیگیری وضعیت سفارش",
            "سلام، لطفاً وضعیت سفارش ثبت‌شده را بررسی کنید.",
        ),
        (
            "راهنمای انتخاب محصول",
            "برای انتخاب محصول مناسب به راهنمایی نیاز دارم.",
        ),
    ]

    tickets_added = 0
    replies_added = 0

    for index, user in enumerate(users[:2]):

        subject, message = topics[index]

        ticket, created = SupportTicket.objects.get_or_create(
            user=user,
            subject=subject,
            defaults={"message": message},
        )

        tickets_added += int(created)

        reply_text = (
            "سلام، درخواست شما دریافت شد. "
            "تیم پشتیبانی ویرا در حال بررسی آن است."
        )

        _reply, reply_created = TicketReply.objects.get_or_create(
            ticket=ticket,
            user=staff,
            message=reply_text,
            defaults={"is_staff_reply": True},
        )

        replies_added += int(reply_created)

    return tickets_added, replies_added


# ============================================================
# FEATURED BRAND
# ============================================================

def create_featured_brand(FeaturedBrand, brand):

    if not FeaturedBrand or not brand:
        return 0

    _obj, created = FeaturedBrand.objects.get_or_create(
        brand=brand,
        defaults={
            "active": True,
            "order": 1,
        },
    )

    return int(created)


# ============================================================
# MAIN
# ============================================================

def main():

    parser = argparse.ArgumentParser(
        description="Create demo data for Vira Online Shop"
    )

    parser.add_argument(
        "--products",
        type=int,
        default=30,
        help="Number of products (1-30)",
    )

    parser.add_argument(
        "--placeholders-only",
        action="store_true",
        help="Generate local SVG images without internet",
    )

    parser.add_argument(
        "--refresh-images",
        action="store_true",
        help="Replace existing demo images",
    )

    args = parser.parse_args()

    if not 1 <= args.products <= len(PRODUCTS):
        parser.error("products must be between 1 and 30")

    global PLACEHOLDERS_ONLY
    PLACEHOLDERS_ONLY = args.placeholders_only

    setup_django()

    from django.conf import settings
    from django.contrib.auth import get_user_model

    User = get_user_model()

    # مدل‌های واقعی پروژه
    BaseCategories = get_model("categories", "BaseCategories")
    Category = get_model("categories", "Category")

    Product = get_model("products", "Product")
    ProductPackage = get_model("products", "ProductPackage")
    Gallery = get_model("products", "Gallery")

    Brand = get_model("public", "Brand")
    Warranty = get_model("public", "Warranty")

    Profile = get_model("account", "Profile")
    ClientAddress = get_model("account", "ClientAddress")
    FavouriteProducts = get_model("account", "FavouriteProducts")
    Notification = get_model(
        "account", "Notification", required=False
    )

    Cart = get_model("cart", "Cart")
    CartItem = get_model("cart", "CartItem")
    Order = get_model("order", "Order")

    Comment = get_model("reviews", "Comment")

    Article = get_model(
        "articles", "Article", required=False
    )

    HomeSlider = get_model(
        "home", "HomeSlider", required=False
    )

    PromotionalBanner = get_model(
        "home", "PromotionalBanner", required=False
    )

    FeaturedBrand = get_model(
        "home", "FeaturedBrand", required=False
    )

    StaticPage = get_model(
        "sitesettings", "StaticPage", required=False
    )

    SupportTicket = get_model(
        "support", "SupportTicket", required=False
    )

    TicketReply = get_model(
        "support", "TicketReply", required=False
    )

    print("\nشروع ساخت داده‌های دمو برای Vira")
    print(f"Media root: {settings.MEDIA_ROOT}")

    print("هیچ داده‌ای حذف نمی‌شود.\n")

    # کاربران و پروفایل‌ها
    users = create_users(User, Profile)

    # دسته‌بندی‌ها
    bases, categories = create_categories(
        BaseCategories,
        Category,
        args.refresh_images,
    )

    # برند و گارانتی
    brand = create_brand(
        Brand,
        categories,
        bases,
    )

    featured_count = create_featured_brand(
        FeaturedBrand,
        brand,
    )

    warranty = create_warranty(Warranty)

    # محصولات و بسته‌های محصول
    products, data_map = create_products(
        Product,
        categories,
        args.products,
        args.refresh_images,
    )

    packages = create_packages(
        products,
        data_map,
        ProductPackage,
        warranty,
        brand,
    )

    # تصاویر گالری
    gallery_count = create_gallery(
        products,
        Gallery,
    )

    # آدرس، سبد خرید و سفارش
    addresses = create_addresses(
        users,
        ClientAddress,
    )

    carts = create_carts(
        users,
        Cart,
    )

    cart_item_count = create_cart_items(
        carts,
        products,
        packages,
        CartItem,
    )

    order_count = create_orders(
        carts,
        users,
        addresses,
        Order,
        CartItem,
    )

    # علاقه‌مندی‌ها و نظرات
    favourite_count = create_favourites(
        users,
        products,
        FavouriteProducts,
    )

    review_count = create_reviews(
        users,
        products,
        Comment,
    )

    # مقالات
    article_count = (
        create_articles(Article, args.refresh_images)
        if Article else 0
    )

    # اسلایدر و بنر
    if HomeSlider and PromotionalBanner:
        slider_count, banner_count = create_home_content(
            HomeSlider,
            PromotionalBanner,
            args.refresh_images,
        )
    else:
        slider_count = banner_count = 0

    # صفحات ثابت
    page_count = (
        create_static_pages(StaticPage)
        if StaticPage else 0
    )

    # اعلان‌ها
    notification_count = (
        create_notifications(users, Notification)
        if Notification else 0
    )

    # پشتیبانی
    if SupportTicket and TicketReply:
        ticket_count, reply_count = create_support(
            users,
            SupportTicket,
            TicketReply,
            User,
        )
    else:
        ticket_count = reply_count = 0

    # گزارش نهایی
    print("\n================ نتیجه نهایی ================")

    print(f"دسته‌های مادر: {len(bases)}")
    print(f"دسته‌بندی‌ها: {len(categories)}")
    print(f"کاربران دمو: {len(users)}")
    print(f"محصولات: {len(products)}")
    print(f"بسته‌های محصول: {len(packages)}")
    print(f"تصاویر گالری جدید: {gallery_count}")

    print(f"آدرس‌های مشتری: {len(addresses)}")
    print(f"سبدهای خرید: {len(carts)}")
    print(f"آیتم‌های سبد خرید جدید: {cart_item_count}")
    print(f"سفارش‌های جدید: {order_count}")

    print(f"علاقه‌مندی‌های جدید: {favourite_count}")
    print(f"نظرات جدید: {review_count}")

    print(f"مقالات جدید: {article_count}")
    print(f"اسلایدرهای جدید: {slider_count}")
    print(f"بنرهای جدید: {banner_count}")
    print(f"برندهای منتخب جدید: {featured_count}")

    print(f"صفحات ثابت جدید: {page_count}")
    print(f"اعلان‌های جدید: {notification_count}")

    print(f"تیکت‌های پشتیبانی جدید: {ticket_count}")
    print(f"پاسخ‌های پشتیبانی جدید: {reply_count}")

    print("\nکاربران:")
    print("vira_demo_01")
    print("vira_demo_02")
    print("vira_demo_03")
    print("vira_demo_04")

    print("\nکاربر پشتیبانی:")
    print("vira_demo_support")

    print("\nرمز حساب‌های تازه‌ساخته‌شده:")
    print("ViraDemo@2026")

    print("==============================================")


if __name__ == "__main__":
    main()
