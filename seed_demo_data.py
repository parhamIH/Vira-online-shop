#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Seed realistic demo data for Vira Online Shop (Django).

Run from the repository root:
    python seed_demo_data.py --inspect
    python seed_demo_data.py --products 30

The script discovers models/fields at runtime instead of assuming a particular
schema. It never deletes existing records. Demo rows are identified by stable
slugs/SKUs, so rerunning the script does not create duplicates.
"""
from __future__ import annotations

import argparse
import importlib.util
import os
import re
import sys
import uuid
from decimal import Decimal
from pathlib import Path
from urllib.error import URLError, HTTPError
from urllib.request import Request, urlopen


# ---------------------------------------------------------------------------
# Django bootstrap
# ---------------------------------------------------------------------------

def bootstrap_django() -> None:
    import django

    supplied = os.environ.get("DJANGO_SETTINGS_MODULE")
    candidates = [supplied] if supplied else []
    candidates += ["main.config.settings", "main.settings", "config.settings"]
    last_error = None
    for module in dict.fromkeys(x for x in candidates if x):
        try:
            if importlib.util.find_spec(module) is None:
                continue
            os.environ["DJANGO_SETTINGS_MODULE"] = module
            django.setup()
            print(f"[Django] settings: {module}")
            return
        except Exception as exc:  # try the next conventional settings module
            last_error = exc
    raise RuntimeError(
        "Django setup failed. Run this file from the folder containing manage.py, "
        "or set DJANGO_SETTINGS_MODULE explicitly. Last error: "
        f"{last_error!r}"
    )


# ---------------------------------------------------------------------------
# Demo catalogue
# ---------------------------------------------------------------------------

PHOTO_IDS = [
    "photo-1523275335684-37898b6baf30",  # watch
    "photo-1542291026-7eec264c27ff",     # sneaker
    "photo-1505740420928-5e560c06d30e",  # headphones
    "photo-1526170375885-4d8ecf77b99f",  # camera
    "photo-1546868871-7041f2a55e12",     # smartwatch
    "photo-1553062407-98eeb64c6a62",     # backpack
    "photo-1585386959984-a4155224a1ad",  # perfume
    "photo-1526170375885-4d8ecf77b99f",  # camera
    "photo-1549298916-b41d501d3772",     # shoes
    "photo-1512499617640-c74ae3a79d37",  # sunglasses
    "photo-1521572163474-6864f9cf17ab",  # t-shirt
    "photo-1529139574466-a303027c1d8b",  # fashion
    "photo-1523381210434-271e8be1f52b",  # clothing
    "photo-1490481651871-ab68de25d43d",  # clothes
    "photo-1503602642458-232111445657",  # chair
    "photo-1494438639946-1ebd1d20bf85",  # home
    "photo-1543163521-1bf539c55dd2",     # shoes
]

CATEGORIES = [
    ("دیجیتال و لوازم جانبی", "digital-accessories"),
    ("پوشاک مردانه", "menswear"),
    ("پوشاک زنانه", "womenswear"),
    ("کیف و کفش", "bags-and-shoes"),
    ("خانه و سبک زندگی", "home-lifestyle"),
    ("زیبایی و سلامت", "beauty-care"),
]

PRODUCTS = [
    ("هدفون بی‌سیم نویزکنسلینگ", "digital-accessories", 3_490_000, 4_200_000, 24),
    ("ساعت هوشمند اسپرت", "digital-accessories", 5_890_000, 6_500_000, 18),
    ("پاوربانک ۲۰۰۰۰ میلی‌آمپر", "digital-accessories", 1_790_000, 2_100_000, 42),
    ("اسپیکر بلوتوث قابل حمل", "digital-accessories", 2_250_000, 2_700_000, 31),
    ("دوربین دیجیتال کامپکت", "digital-accessories", 18_900_000, 21_000_000, 7),
    ("ماوس بی‌سیم ارگونومیک", "digital-accessories", 890_000, 1_050_000, 55),
    ("کیبورد مکانیکی", "digital-accessories", 3_150_000, 3_600_000, 16),
    ("شارژر سریع USB-C", "digital-accessories", 690_000, 850_000, 63),
    ("عینک آفتابی کلاسیک", "bags-and-shoes", 1_250_000, 1_500_000, 29),
    ("کوله‌پشتی روزمره", "bags-and-shoes", 2_450_000, 2_900_000, 14),
    ("کتانی روزمره سفید", "bags-and-shoes", 3_850_000, 4_400_000, 21),
    ("کفش پیاده‌روی", "bags-and-shoes", 4_290_000, 4_900_000, 12),
    ("تی‌شرت ساده پنبه‌ای", "menswear", 590_000, 750_000, 80),
    ("هودی دورس مینیمال", "menswear", 1_890_000, 2_200_000, 26),
    ("پیراهن آستین‌بلند", "menswear", 1_350_000, 1_600_000, 19),
    ("شلوار جین راسته", "menswear", 1_990_000, 2_300_000, 22),
    ("مانتو روزمره", "womenswear", 2_750_000, 3_200_000, 15),
    ("شومیز لینن", "womenswear", 1_450_000, 1_750_000, 23),
    ("کیف دستی مینیمال", "womenswear", 2_190_000, 2_600_000, 11),
    ("شال نخی چهارفصل", "womenswear", 490_000, 620_000, 47),
    ("چراغ مطالعه رومیزی", "home-lifestyle", 1_150_000, 1_400_000, 17),
    ("ماگ سرامیکی", "home-lifestyle", 320_000, 420_000, 65),
    ("بطری آب استیل", "home-lifestyle", 780_000, 950_000, 34),
    ("کوسن دکوراتیو", "home-lifestyle", 560_000, 690_000, 38),
    ("عطر روزانه مردانه", "beauty-care", 2_650_000, 3_100_000, 9),
    ("عطر ملایم زنانه", "beauty-care", 2_890_000, 3_300_000, 13),
    ("کرم مرطوب‌کننده", "beauty-care", 420_000, 520_000, 44),
    ("ست مراقبت پوست", "beauty-care", 1_750_000, 2_050_000, 20),
    ("کیف پول چرمی", "bags-and-shoes", 1_090_000, 1_300_000, 27),
    ("هدفون روگوشی استودیویی", "digital-accessories", 4_750_000, 5_400_000, 8),
]

# Source photos are downloaded into Django's MEDIA_ROOT by the running script.
# If network access is unavailable, a clean SVG product placeholder is saved.
PHOTO_URLS = [
    f"https://images.unsplash.com/{photo_id}?auto=format&fit=crop&w=1000&q=85"
    for photo_id in PHOTO_IDS if " " not in photo_id
]


# ---------------------------------------------------------------------------
# Generic model helpers
# ---------------------------------------------------------------------------

def norm(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", value.lower())


def discover_model(model_names, app_hint=None):
    from django.apps import apps
    wanted = {norm(x) for x in model_names}
    matches = [m for m in apps.get_models() if norm(m.__name__) in wanted]
    if app_hint:
        hinted = [m for m in matches if app_hint in m._meta.label_lower]
        if hinted:
            matches = hinted
    return matches[0] if matches else None


def get_concrete_fields(model):
    return [f for f in model._meta.get_fields()
            if getattr(f, "concrete", False) and not getattr(f, "auto_created", False)]


def find_field(model, names):
    wanted = {norm(x) for x in names}
    for field in get_concrete_fields(model):
        if norm(field.name) in wanted:
            return field
    return None


def field_is_file(field):
    try:
        from django.db import models
        return isinstance(field, (models.FileField, models.ImageField))
    except Exception:
        return False


def safe_slug(text: str) -> str:
    from django.utils.text import slugify
    value = slugify(text, allow_unicode=True)
    return value or f"demo-{uuid.uuid4().hex[:8]}"


def print_model_report():
    from django.apps import apps
    print("\n=== Django model/field inspection ===")
    for model in sorted(apps.get_models(), key=lambda x: x._meta.label_lower):
        print(f"\n[{model._meta.label}]")
        for field in get_concrete_fields(model):
            if field.primary_key:
                continue
            kind = field.get_internal_type()
            flags = []
            if field.null:
                flags.append("nullable")
            if field.blank:
                flags.append("blank")
            if field.has_default():
                flags.append("default")
            if getattr(field, "unique", False):
                flags.append("unique")
            if field.is_relation and getattr(field, "many_to_one", False):
                kind += f" -> {field.remote_field.model._meta.label}"
            if field_is_file(field):
                kind += " [FILE]"
            print(f"  - {field.name}: {kind}" + (f" ({', '.join(flags)})" if flags else ""))
        for field in model._meta.many_to_many:
            print(f"  - {field.name}: MANY-TO-MANY -> {field.remote_field.model._meta.label}")
    print("\n======================================\n")


def placeholder_svg(title: str, index: int) -> bytes:
    # Browser-renderable fallback. Real product photos are preferred and are
    # downloaded automatically whenever the machine can reach images.unsplash.com.
    backgrounds = ["#e9edf5", "#f0e9e2", "#e5eee9", "#f1e9ef", "#e9eef0"]
    bg = backgrounds[index % len(backgrounds)]
    clean = (title.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))[:70]
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="1000" viewBox="0 0 1000 1000">
    <rect width="1000" height="1000" fill="{bg}"/>
    <circle cx="500" cy="390" r="170" fill="#ffffff" opacity=".7"/>
    <rect x="310" y="245" width="380" height="300" rx="55" fill="#64748b" opacity=".17"/>
    <text x="500" y="720" text-anchor="middle" font-family="Tahoma,Arial,sans-serif" font-size="42" fill="#273449">{clean}</text>
    <text x="500" y="790" text-anchor="middle" font-family="Arial,sans-serif" font-size="26" fill="#64748b">VIRA DEMO PRODUCT</text>
    </svg>'''
    return svg.encode("utf-8")


_IMAGE_CACHE = {}


def fetch_photo(index: int, title: str) -> tuple[bytes, str]:
    if index in _IMAGE_CACHE:
        return _IMAGE_CACHE[index]
    if PHOTO_URLS:
        url = PHOTO_URLS[index % len(PHOTO_URLS)]
        try:
            request = Request(url, headers={"User-Agent": "ViraDemoSeeder/1.0"})
            with urlopen(request, timeout=12) as response:
                data = response.read()
                content_type = response.headers.get("Content-Type", "")
                if response.status == 200 and content_type.startswith("image/") and len(data) > 4_000:
                    result = (data, ".jpg")
                    _IMAGE_CACHE[index] = result
                    return result
        except (URLError, HTTPError, TimeoutError, OSError):
            pass
    result = (placeholder_svg(title, index), ".svg")
    _IMAGE_CACHE[index] = result
    return result


def pick_choice(field, desired_words):
    choices = list(getattr(field, "choices", []) or [])
    if not choices:
        return None
    for value, label in choices:
        text = f"{value} {label}".lower()
        if any(word in text for word in desired_words):
            return value
    return choices[0][0]


def semantic_value(field, semantics):
    """Find a supplied semantic value for this concrete model field."""
    aliases = {
        "name": ["name", "title", "product_name", "full_name", "label"],
        "title": ["title", "name", "product_name"],
        "slug": ["slug"],
        "description": ["description", "details", "detail", "content", "short_description"],
        "price": ["price", "unit_price", "selling_price", "sale_price", "final_price", "amount"],
        "old_price": ["old_price", "original_price", "market_price", "compare_at_price", "base_price", "list_price"],
        "sku": ["sku", "product_code", "code", "barcode"],
        "stock": ["stock", "inventory", "quantity", "stock_quantity", "inventory_count"],
        "image": ["image", "main_image", "thumbnail", "photo", "cover", "picture"],
        "email": ["email", "email_address"],
        "username": ["username", "user_name", "login", "phone"],
        "phone": ["phone", "mobile", "mobile_number", "phone_number"],
        "status": ["status", "state", "order_status", "payment_status"],
        "rating": ["rating", "rate", "score", "stars"],
        "quantity": ["quantity", "qty", "count"],
        "is_active": ["is_active", "active", "is_available", "available", "is_published", "published"],
    }
    fname = norm(field.name)
    for semantic, candidate_names in aliases.items():
        if fname in {norm(x) for x in candidate_names} and semantic in semantics:
            return semantics[semantic], True
    if field.name in semantics:
        return semantics[field.name], True
    return None, False


def generic_required_value(field, model, stable_key, index=0):
    """Supply conservative defaults for non-null, non-optional model fields."""
    from django.db import models
    from django.utils import timezone

    kind = field.get_internal_type()
    name = norm(field.name)

    if getattr(field, "choices", None):
        if any(x in name for x in ("status", "state")):
            return pick_choice(field, ["publish", "active", "available", "complete", "approved", "pending"])
        if "role" in name or "type" in name:
            return pick_choice(field, ["customer", "client", "user", "buyer"])
        return pick_choice(field, [])
    if kind in ("BooleanField", "NullBooleanField"):
        return any(x in name for x in ("active", "available", "published", "verified", "enabled"))
    if kind in ("DateTimeField",):
        return timezone.now()
    if kind == "DateField":
        return timezone.localdate()
    if kind == "TimeField":
        return timezone.now().time().replace(microsecond=0)
    if kind in ("DecimalField", "FloatField"):
        if any(x in name for x in ("price", "amount", "total", "cost", "fee")):
            return Decimal("100000") if kind == "DecimalField" else 100000.0
        return Decimal("0") if kind == "DecimalField" else 0.0
    if kind in ("IntegerField", "PositiveIntegerField", "PositiveSmallIntegerField", "SmallIntegerField", "BigIntegerField"):
        if any(x in name for x in ("stock", "quantity", "count", "inventory")):
            return 10
        if any(x in name for x in ("rating", "rate", "score")):
            return 5
        return 0
    if kind in ("JSONField",):
        return {}
    if kind == "UUIDField":
        return uuid.uuid4()
    if kind in ("EmailField",):
        return f"{safe_slug(stable_key)}-{index}@vira-demo.local"
    if kind in ("URLField",):
        return "https://example.com/demo"
    if kind in ("TextField",):
        return f"اطلاعات نمونه برای نمایش فروشگاه ویرا؛ {stable_key}."
    if kind in ("CharField", "SlugField"):
        if "slug" in name:
            return safe_slug(stable_key)
        if "email" in name:
            return f"{safe_slug(stable_key)}-{index}@vira-demo.local"
        if any(x in name for x in ("phone", "mobile")):
            return f"0912000{index:04d}"
        if any(x in name for x in ("sku", "barcode", "code")):
            return f"VIRA-DEMO-{index:04d}"
        if any(x in name for x in ("name", "title", "label")):
            return f"نمونه {stable_key}"
        return f"Demo {field.name} {index + 1}"
    return None


def coerce_choice(field, value):
    choices = list(getattr(field, "choices", []) or [])
    if not choices or value is None:
        return value
    for choice_value, _label in choices:
        if str(choice_value).lower() == str(value).lower():
            return choice_value
    requested = str(value).lower()
    # Try matching the requested status/value against stored value + display label.
    for choice_value, label in choices:
        if requested in f"{choice_value} {label}".lower():
            return choice_value
    synonyms = {
        "published": ["publish", "active", "visible", "approved"],
        "active": ["active", "enabled", "available"],
        "delivered": ["deliver", "complete", "received"],
        "processing": ["process", "prepar", "progress"],
        "pending": ["pending", "await", "new"],
        "cancelled": ["cancel", "reject"],
        "approved": ["approv", "accept", "publish"],
    }
    return pick_choice(field, synonyms.get(requested, [requested]))


def build_values(model, semantics, relations, stable_key, index=0):
    """Build kwargs based on real model fields and discovered related objects."""
    values = {}
    for field in get_concrete_fields(model):
        if field.primary_key or getattr(field, "auto_created", False):
            continue
        if field.name in semantics:
            values[field.name] = coerce_choice(field, semantics[field.name])
            continue
        if field_is_file(field):
            continue
        if getattr(field, "many_to_one", False) or getattr(field, "one_to_one", False):
            related = field.remote_field.model
            if related in relations:
                values[field.name] = relations[related]
                continue
            if field.null or field.has_default() or field.blank:
                continue
            # Avoid guessing foreign keys to addresses, providers, etc.
            continue
        if field.many_to_many:
            continue
        value, found = semantic_value(field, semantics)
        if found:
            values[field.name] = coerce_choice(field, value)
            continue
        if field.has_default() or field.null:
            continue
        fallback = generic_required_value(field, model, stable_key, index)
        if fallback is not None:
            values[field.name] = fallback
    return values


def stable_lookup(model, semantics, fallback_name=None):
    """Return a repeatable lookup key without relying on auto-generated IDs."""
    preferred = ["slug", "sku", "order_number", "tracking_code", "reference", "code", "username", "email", "name", "title"]
    for name in preferred:
        field = find_field(model, [name])
        if not field:
            continue
        value = semantics.get(field.name)
        if value not in (None, ""):
            return {field.name: value}
    if fallback_name:
        field = find_field(model, ["name", "title", "username", "email"])
        if field:
            return {field.name: fallback_name}
    return None


def attach_file(instance, field, data, file_ext, stem):
    from django.core.files.base import ContentFile
    filename = f"{safe_slug(stem)}{file_ext}"
    getattr(instance, field.name).save(filename, ContentFile(data), save=False)


REFRESH_IMAGES = False

def create_or_get(model, semantics, relations=None, image=None, stable_key="demo", index=0, update=False):
    """Create one record; return (object, created). Existing records are kept."""
    relations = relations or {}
    lookup = stable_lookup(model, semantics, stable_key)
    if lookup:
        try:
            current = model._default_manager.filter(**lookup).first()
            if current is not None:
                if image and REFRESH_IMAGES:
                    image_fields = [f for f in get_concrete_fields(model) if field_is_file(f)]
                    preferred = [f for f in image_fields if any(
                        x in norm(f.name) for x in ("image", "photo", "picture", "cover", "thumbnail")
                    )]
                    target = preferred[0] if preferred else (image_fields[0] if image_fields else None)
                    if target is not None:
                        data, ext = image
                        attach_file(current, target, data, ext, stable_key)
                        current.save(update_fields=[target.name])
                return current, False
        except Exception:
            pass

    values = build_values(model, semantics, relations, stable_key, index)
    instance = model(**values)
    if image:
        data, ext = image
        image_fields = [f for f in get_concrete_fields(model) if field_is_file(f)]
        # Prefer a product's primary image field; do not fill every optional file field.
        preferred = [f for f in image_fields if any(
            x in norm(f.name) for x in ("image", "photo", "picture", "cover", "thumbnail")
        )]
        target = preferred[0] if preferred else (image_fields[0] if image_fields else None)
        if target is not None:
            attach_file(instance, target, data, ext, stable_key)

    instance.save()

    # Populate M2M category/tag relations only when the field matches a known model.
    for m2m in model._meta.many_to_many:
        related_model = m2m.remote_field.model
        if related_model in relations and any(x in norm(m2m.name) for x in ("category", "brand", "tag")):
            getattr(instance, m2m.name).add(relations[related_model])
    return instance, True


def create_demo_users(count=4):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    users = []
    username_field = getattr(User, "USERNAME_FIELD", "username")
    for idx in range(1, count + 1):
        username = f"vira_demo_{idx:02d}"
        email = f"customer{idx:02d}@vira-demo.local"
        identifier_field = find_field(User, [username_field])
        phone = f"0912111{idx:04d}"
        username_field_norm = norm(username_field)
        is_phone_identifier = any(token in username_field_norm for token in ("phone", "mobile", "tel"))
        identifier = email if username_field == "email" else (phone if is_phone_identifier else username)
        lookup = {username_field: identifier}
        existing = User._default_manager.filter(**lookup).first()
        if existing:
            users.append(existing)
            continue
        semantics = {
            "username": username,
            "email": email,
            "phone": phone,
            "name": f"مشتری دمو {idx}",
            "first_name": f"مشتری{idx}",
            "last_name": "نمونه",
            "is_active": True,
            "is_staff": False,
            "is_superuser": False,
        }
        if identifier_field and username_field not in semantics:
            semantics[username_field] = lookup[username_field]
        try:
            from django.db import transaction
            with transaction.atomic():
                values = build_values(User, semantics, {}, username, idx)
                # Username/email values must match the unique identifier above.
                if identifier_field:
                    values[username_field] = lookup[username_field]
                user = User(**values)
                if hasattr(user, "set_password"):
                    user.set_password("ViraDemo@2026")
                elif find_field(User, ["password"]):
                    user.password = "ViraDemo@2026"
                user.save()
            users.append(user)
        except Exception as exc:
            print(f"  [WARN] کاربر دمو {idx} ساخته نشد: {exc}")
    return users


def create_categories(Category):
    categories = {}
    for idx, (name, slug) in enumerate(CATEGORIES):
        semantics = {
            "name": name,
            "title": name,
            "slug": slug,
            "description": f"مجموعه محصولات دسته {name} در فروشگاه ویرا.",
            "is_active": True,
            "is_published": True,
        }
        try:
            from django.db import transaction
            with transaction.atomic():
                category, created = create_or_get(
                    Category, semantics, stable_key=slug, index=idx,
                )
            categories[slug] = category
            print(f"  [{'NEW' if created else 'EXISTS'}] دسته: {name}")
        except Exception as exc:
            print(f"  [WARN] دسته «{name}» ساخته نشد: {exc}")
    return categories


def create_products(Product, Category, categories, count=30, Brand=None):
    brands = {}
    brand_obj = None
    if Brand:
        try:
            from django.db import transaction
            with transaction.atomic():
                brand_obj, _ = create_or_get(
                    Brand,
                    {"name": "ویرا", "title": "ویرا", "slug": "vira-demo-brand", "is_active": True},
                    stable_key="vira-demo-brand",
                )
            brands[Brand] = brand_obj
        except Exception as exc:
            print(f"  [WARN] برند نمونه ساخته نشد: {exc}")

    created_products = []
    data = PRODUCTS[:max(0, count)]
    if count > len(PRODUCTS):
        print(f"  [INFO] فقط {len(PRODUCTS)} محصول آماده در دیتاست تعریف شده است.")
    for idx, (name, category_slug, price, old_price, stock) in enumerate(data):
        slug = safe_slug(name)
        category = categories.get(category_slug)
        semantics = {
            "name": name,
            "title": name,
            "product_name": name,
            "slug": slug,
            "sku": f"VIRA-DEMO-{idx + 1:04d}",
            "code": f"VIRA-DEMO-{idx + 1:04d}",
            "description": (
                f"{name} با طراحی کاربردی و کیفیت مناسب. این محصول برای نمایش امکانات "
                "فروشگاه اینترنتی ویرا در محیط دمو ثبت شده است."
            ),
            "short_description": f"{name}؛ انتخابی کاربردی برای استفاده روزمره.",
            "price": Decimal(price),
            "old_price": Decimal(old_price),
            "original_price": Decimal(old_price),
            "stock": stock,
            "quantity": stock,
            "stock_quantity": stock,
            "is_active": True,
            "is_available": True,
            "is_published": True,
            "published": True,
            "is_featured": idx < 8,
            "featured": idx < 8,
            "status": "published",
        }
        relations = {}
        if category is not None:
            relations[Category] = category
        relations.update(brands)
        photo = fetch_photo(idx, name)
        try:
            from django.db import transaction
            with transaction.atomic():
                product, created = create_or_get(
                    Product, semantics, relations=relations, image=photo,
                    stable_key=slug, index=idx,
                )
            created_products.append(product)
            print(f"  [{'NEW' if created else 'EXISTS'}] محصول: {name}")
        except Exception as exc:
            print(f"  [ERROR] محصول «{name}» ساخته نشد: {exc}")
    return created_products


def create_product_gallery(products):
    from django.db import IntegrityError, transaction
    Gallery = discover_model(
        ["ProductImage", "ProductGallery", "ProductImageGallery", "GalleryImage"],
        app_hint="product",
    )
    if not Gallery:
        return 0
    ProductModel = products[0].__class__ if products else None
    if ProductModel is None:
        return 0
    added = 0
    for idx, product in enumerate(products[:20]):
        try:
            # Do not add the same gallery image twice on subsequent runs.
            pfield = next((f for f in get_concrete_fields(Gallery)
                           if getattr(f, "many_to_one", False)
                           and f.remote_field.model == ProductModel), None)
            if not pfield:
                continue
            existing = Gallery._default_manager.filter(**{pfield.name: product}).exists()
            if existing:
                continue
            image = fetch_photo(idx + 3, product.__str__())
            with transaction.atomic():
                _, created = create_or_get(
                    Gallery,
                    {pfield.name: product, "title": f"تصویر {idx + 1}"},
                    relations={ProductModel: product},
                    image=image,
                    stable_key=f"gallery-{product.pk}", index=idx,
                )
            added += int(created)
        except Exception as exc:
            print(f"  [WARN] تصویر گالری برای {product} ثبت نشد: {exc}")
    return added



def create_optional_rows(model_names, relation_pools, rows, label):
    """Populate optional models only when their required FK graph is available.

    This lets the same script support different Vira schema revisions without
    blindly creating records in unrelated/custom tables.
    """
    from django.db import transaction
    Model = discover_model(model_names)
    if not Model:
        return []

    made = []
    for idx, row in enumerate(rows):
        relations = {}
        relation_lookup = {}
        missing = []
        for field in get_concrete_fields(Model):
            if not (getattr(field, "many_to_one", False) or getattr(field, "one_to_one", False)):
                continue
            related_model = field.remote_field.model
            pool = relation_pools.get(related_model)
            if pool:
                related_obj = pool[idx % len(pool)] if isinstance(pool, (list, tuple)) else pool
                relations[related_model] = related_obj
                relation_lookup[field.name] = related_obj
            elif not field.null and not field.has_default():
                missing.append(f"{field.name}->{related_model._meta.label}")
        if missing:
            if idx == 0:
                print(f"  [SKIP] {label}: فیلدهای رابطه‌ای لازم در دسترس نیستند: {', '.join(missing)}")
            continue

        semantics = dict(row)
        stable_key = semantics.get("slug") or semantics.get("order_number") or semantics.get("sku") or semantics.get("title") or f"{label}-{idx + 1}"
        try:
            with transaction.atomic():
                existing = None
                if relation_lookup:
                    existing = Model._default_manager.filter(**relation_lookup).first()
                if existing is not None:
                    made.append(existing)
                    continue
                obj, created = create_or_get(
                    Model,
                    semantics,
                    relations=relations,
                    stable_key=str(stable_key),
                    index=idx,
                )
            made.append(obj)
            print(f"  [{'NEW' if created else 'EXISTS'}] {label}: {obj}")
        except Exception as exc:
            if idx == 0:
                print(f"  [SKIP] {label}: مدل پیدا شد، اما ساخت رکورد با فیلدهای فعلی ممکن نشد: {exc}")
    return made


def create_demo_transactions(products, users):
    """Try to create orders, order lines, carts, reviews and wishlists when present."""
    from django.contrib.auth import get_user_model
    User = get_user_model()
    Product = products[0].__class__ if products else None
    if Product is None:
        return {}

    result = {}
    orders_model = discover_model(["Order", "CustomerOrder", "ShopOrder"], app_hint="order")
    carts_model = discover_model(["Cart", "ShoppingCart", "Basket"], app_hint="cart")
    wishlists_model = discover_model(["Wishlist", "WishList", "FavoriteList"])

    order_rows = []
    for idx in range(min(len(users), 4)):
        order_rows.append({
            "order_number": f"VIRA-DEMO-ORDER-{idx + 1:04d}",
            "number": f"VIRA-DEMO-ORDER-{idx + 1:04d}",
            "reference": f"VIRA-DEMO-ORDER-{idx + 1:04d}",
            "slug": f"vira-demo-order-{idx + 1:04d}",
            "title": f"سفارش آزمایشی {idx + 1}",
            "status": ["delivered", "processing", "pending", "cancelled"][idx % 4],
            "total": Decimal(3_500_000 + idx * 1_250_000),
            "total_price": Decimal(3_500_000 + idx * 1_250_000),
            "grand_total": Decimal(3_500_000 + idx * 1_250_000),
            "subtotal": Decimal(3_500_000 + idx * 1_250_000),
            "discount": Decimal("0"),
            "shipping_cost": Decimal("0"),
            "is_paid": idx != 2,
            "is_active": True,
        })
    order_pools = {User: users}
    orders = create_optional_rows(["Order", "CustomerOrder", "ShopOrder"], order_pools, order_rows, "سفارش")
    result["orders"] = len(orders)

    if orders:
        order_item_rows = []
        for idx, order in enumerate(orders):
            for line in range(2):
                p = products[(idx * 2 + line) % len(products)]
                order_item_rows.append({
                    "title": f"ردیف سفارش {idx + 1}-{line + 1}",
                    "quantity": 1 + line,
                    "qty": 1 + line,
                    "price": Decimal(1_250_000 + line * 500_000),
                    "unit_price": Decimal(1_250_000 + line * 500_000),
                    "total": Decimal(1_250_000 + line * 500_000) * (1 + line),
                    "subtotal": Decimal(1_250_000 + line * 500_000) * (1 + line),
                    "sku": f"VIRA-DEMO-ORDER-LINE-{idx + 1:02d}-{line + 1}",
                })
        # Pair order and product by using interleaved pools.
        order_pool = [o for o in orders for _ in range(2)]
        product_pool = [products[(i * 2 + j) % len(products)] for i in range(len(orders)) for j in range(2)]
        OrderModel = orders[0].__class__
        order_items = create_optional_rows(
            ["OrderItem", "OrderLine", "OrderDetail", "PurchasedItem"],
            {OrderModel: order_pool, Product: product_pool},
            order_item_rows,
            "آیتم سفارش",
        )
        result["order_items"] = len(order_items)

    # Active carts and cart lines (only where the schema has compatible relations).
    cart_rows = [
        {"title": f"سبد خرید دمو {idx + 1}", "name": f"سبد خرید دمو {idx + 1}", "is_active": True,
         "session_key": f"vira-demo-session-{idx + 1}"}
        for idx in range(min(len(users), 4))
    ]
    carts = create_optional_rows(["Cart", "ShoppingCart", "Basket"], {User: users}, cart_rows, "سبد خرید")
    result["carts"] = len(carts)
    if carts:
        cart_rows_items = []
        cart_pool = []
        product_pool = []
        for idx, cart in enumerate(carts):
            for line in range(2):
                cart_pool.append(cart)
                product_pool.append(products[(idx * 3 + line) % len(products)])
                cart_rows_items.append({
                    "title": f"محصول سبد {idx + 1}-{line + 1}",
                    "quantity": line + 1,
                    "qty": line + 1,
                    "price": Decimal(890_000 + line * 450_000),
                    "unit_price": Decimal(890_000 + line * 450_000),
                    "sku": f"VIRA-DEMO-CART-{idx + 1:02d}-{line + 1}",
                })
        CartModel = carts[0].__class__
        cart_items = create_optional_rows(
            ["CartItem", "BasketItem", "ShoppingCartItem"],
            {CartModel: cart_pool, Product: product_pool},
            cart_rows_items,
            "آیتم سبد خرید",
        )
        result["cart_items"] = len(cart_items)

    # Product reviews. One review per user/product pair if a compatible model exists.
    review_rows = []
    review_users, review_products = [], []
    for idx in range(min(12, len(products), len(users) * 3)):
        review_users.append(users[idx % len(users)])
        review_products.append(products[idx])
        review_rows.append({
            "title": f"نظر مشتری دمو {idx + 1}",
            "subject": f"تجربه خرید {idx + 1}",
            "comment": "کیفیت محصول مناسب بود و تجربه خرید خوبی داشتم.",
            "content": "کیفیت محصول مناسب بود و تجربه خرید خوبی داشتم.",
            "body": "کیفیت محصول مناسب بود و تجربه خرید خوبی داشتم.",
            "text": "کیفیت محصول مناسب بود و تجربه خرید خوبی داشتم.",
            "rating": 4 + (idx % 2),
            "score": 4 + (idx % 2),
            "is_approved": True,
            "is_active": True,
            "status": "approved",
        })
    reviews = create_optional_rows(
        ["ProductReview", "Review", "ProductRating", "Comment"],
        {User: review_users, Product: review_products},
        review_rows,
        "نظر محصول",
    )
    result["reviews"] = len(reviews)

    # Wishlist/favorites are also optional and only seeded if both user and product links exist.
    wishlist_rows = [
        {"title": f"علاقه‌مندی دمو {idx + 1}", "name": f"علاقه‌مندی دمو {idx + 1}",
         "is_active": True, "quantity": 1}
        for idx in range(min(len(users), 4))
    ]
    wishlists = create_optional_rows(
        ["Wishlist", "WishList", "FavoriteList"], {User: users}, wishlist_rows, "لیست علاقه‌مندی"
    )
    result["wishlists"] = len(wishlists)
    if wishlists:
        wishlist_items_rows, wishlist_pool, product_pool = [], [], []
        for idx, wishlist in enumerate(wishlists):
            wishlist_pool.append(wishlist)
            product_pool.append(products[(idx + 5) % len(products)])
            wishlist_items_rows.append({
                "title": f"علاقه‌مندی محصول {idx + 1}",
                "quantity": 1,
                "sku": f"VIRA-DEMO-WISH-{idx + 1:02d}",
            })
        WishlistModel = wishlists[0].__class__
        wishlist_items = create_optional_rows(
            ["WishlistItem", "WishListItem", "FavoriteItem"],
            {WishlistModel: wishlist_pool, Product: product_pool},
            wishlist_items_rows,
            "آیتم علاقه‌مندی",
        )
        result["wishlist_items"] = len(wishlist_items)

    return result

def main():
    parser = argparse.ArgumentParser(description="Create demo catalogue data for Vira Online Shop")
    parser.add_argument("--inspect", action="store_true", help="Only list actual Django models and their fields")
    parser.add_argument("--products", type=int, default=30, help="Number of demo products (1-30; default: 30)")
    parser.add_argument("--placeholders-only", action="store_true", help="Use local SVG placeholders instead of downloading photos")
    parser.add_argument("--refresh-images", action="store_true", help="Replace existing product images with newly downloaded/local images")
    args = parser.parse_args()

    if not 1 <= args.products <= len(PRODUCTS):
        parser.error(f"--products must be between 1 and {len(PRODUCTS)}")

    bootstrap_django()
    from django.apps import apps
    from django.conf import settings
    from django.db import transaction

    if args.inspect:
        print_model_report()
        return

    Product = discover_model(["Product", "Products"], app_hint="product")
    Category = discover_model(["Category", "Categories", "ProductCategory", "ProductCategories"], app_hint="categor")
    Brand = discover_model(["Brand", "Brands", "ProductBrand"], app_hint="product")

    if not Product:
        print("[ERROR] مدل Product در اپ‌های نصب‌شده پیدا نشد.")
        print("ابتدا دستور زیر را اجرا کنید تا مدل‌ها و فیلدهای واقعی چاپ شوند:")
        print("    python seed_demo_data.py --inspect")
        sys.exit(2)
    if not Category:
        print("[WARN] مدل Category پیدا نشد؛ محصولات بدون اتصال دسته ساخته می‌شوند.")

    print("\nشروع ساخت داده‌های دمو برای Vira Online Shop")
    print(f"Product model: {Product._meta.label}")
    print(f"Category model: {Category._meta.label if Category else 'NOT FOUND'}")
    print(f"Media root: {getattr(settings, 'MEDIA_ROOT', '(not configured)')}")
    print("نکته: هیچ داده‌ای حذف نمی‌شود. اجرای دوباره، رکوردهای دمو را تکراری نمی‌کند.\n")

    if args.placeholders_only:
        _IMAGE_CACHE.clear()
        global fetch_photo
        fetch_photo = lambda index, title: (placeholder_svg(title, index), ".svg")

    global REFRESH_IMAGES
    REFRESH_IMAGES = args.refresh_images

    with transaction.atomic():
        categories = create_categories(Category) if Category else {}
        users = create_demo_users(4)
        products = create_products(Product, Category, categories, args.products, Brand)
        gallery_count = create_product_gallery(products)
        extras = create_demo_transactions(products, users)

    print("\n========== نتیجه ==========")
    print(f"دسته‌های تعریف‌شده: {len(categories)}")
    print(f"کاربران دمو: {len(users)}")
    print(f"محصولات موجود/ساخته‌شده: {len(products)}")
    print(f"تصاویر گالری اضافه‌شده: {gallery_count}")
    for key, value in extras.items():
        print(f"{key}: {value}")
    print("رمز عبور کاربران دمو: ViraDemo@2026")
    print("این رمز را فقط در محیط توسعه/دمو استفاده کنید.")
    print("===========================")


if __name__ == "__main__":
    main()
