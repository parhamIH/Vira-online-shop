import os
import django
import random
from faker import Faker
import datetime
from pathlib import Path

# Django settings must be configured before importing models
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "main.settings")
django.setup()

# Now it's safe to import Django models
from django.core.files import File
from django.contrib.auth.models import User
from django.utils.text import slugify

from shopApp.models import (
    BaseCategorys, Category, Brand, Color, BaseColor, 
    Size, Product, ProductPackage, Gallery,
    HomeSlider, PromotionalBanner, FeaturedBrand
)
from account.models import UserCoupon

def cleanup_existing_data():
    """پاک کردن داده‌های موجود برای جلوگیری از تداخل در ساخت مجدد"""
    print("در حال پاک کردن داده‌های قبلی...")
    
    # حذف همه موارد به ترتیب وابستگی
    Gallery.objects.all().delete()
    ProductPackage.objects.all().delete()
    Product.objects.all().delete()
    PromotionalBanner.objects.all().delete()
    HomeSlider.objects.all().delete()
    FeaturedBrand.objects.all().delete()
    Size.objects.all().delete()
    Color.objects.all().delete()
    BaseColor.objects.all().delete()
    Brand.objects.all().delete()
    Category.objects.all().delete()
    BaseCategorys.objects.all().delete()
    
    print("تمام داده‌های قبلی با موفقیت حذف شدند.")

def create_demo_data():
    print("شروع ایجاد داده‌های نمایشی...")
    
    # پاک کردن داده‌های موجود قبل از ایجاد داده‌های جدید
    cleanup_existing_data()
    
    fake = Faker(['fa_IR'])
    
    # تعریف مسیر تصویر پیش‌فرض
    default_img_path = Path('C:/Users/Padidar/Desktop/ChatGPT Image Apr 2, 2025, 06_33_09 PM.png')
    use_images = default_img_path.exists()
    
    if not use_images:
        print("تصویر پیش‌فرض یافت نشد. محصولات بدون تصویر ایجاد خواهند شد.")
    
    # ایجاد کاربر ادمین
    try:
        admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123'
        )
        print("کاربر ادمین ایجاد شد.")
    except:
        admin_user = User.objects.get(username='admin')
        print("کاربر ادمین از قبل وجود دارد.")
    
    # افزودن کوپن تستی برای همه کاربران
    all_users = User.objects.all()
    for user in all_users:
        for i in range(2):
            UserCoupon.objects.create(
                user=user,
                code=f"TESTCOUPON{user.id}{i+1}",
                discount=random.choice([10, 15, 20, 25]),
                is_active=random.choice([True, False]),
                expire_at=datetime.datetime.now() + datetime.timedelta(days=random.randint(5, 30))
            )
    print("کوپن‌های تستی برای کاربران ایجاد شد.")
    
    # ایجاد دسته‌بندی‌های اصلی
    base_categories = [
        {
            'name': 'زیورآلات', 
            'en_name': 'jewelry', 
            'description': 'انواع زیورآلات شامل گردنبند، دستبند، انگشتر و گوشواره'
        },
        {
            'name': 'کیف و کفش', 
            'en_name': 'bags-shoes', 
            'description': 'انواع کیف و کفش زنانه و مردانه'
        },
        {
            'name': 'ساعت', 
            'en_name': 'watches', 
            'description': 'انواع ساعت‌های مچی مردانه و زنانه'
        },
        {
            'name': 'عینک', 
            'en_name': 'glasses', 
            'description': 'انواع عینک‌های آفتابی و طبی'
        },
        {
            'name': 'اکسسوری موبایل', 
            'en_name': 'mobile-accessories', 
            'description': 'اکسسوری‌های موبایل شامل قاب، محافظ صفحه و غیره'
        }
    ]
    
    created_base_categories = []
    for cat in base_categories:
        # ایجاد دسته‌بندی اصلی بدون تصویر
        base_category = BaseCategorys.objects.create(
            name=cat['name'],
            en_name=cat['en_name'],
            description=cat['description']
        )
        
        # اضافه کردن تصویر در صورت وجود
        if use_images:
            try:
                with open(default_img_path, 'rb') as img_file:
                    base_category.image.save(f"{cat['en_name']}.png", File(img_file))
            except Exception as e:
                print(f"خطا در اضافه کردن تصویر به دسته‌بندی {cat['name']}: {str(e)}")
        
        created_base_categories.append(base_category)
        print(f"دسته‌بندی اصلی {cat['name']} ایجاد شد.")
    
    # ایجاد زیردسته‌ها
    subcategories = {
        'jewelry': [
            {'name': 'گردنبند', 'en_name': 'necklace'},
            {'name': 'دستبند', 'en_name': 'bracelet'},
            {'name': 'انگشتر', 'en_name': 'ring'},
            {'name': 'گوشواره', 'en_name': 'earring'}
        ],
        'bags-shoes': [
            {'name': 'کیف زنانه', 'en_name': 'womens-bags'},
            {'name': 'کیف مردانه', 'en_name': 'mens-bags'},
            {'name': 'کفش زنانه', 'en_name': 'womens-shoes'},
            {'name': 'کفش مردانه', 'en_name': 'mens-shoes'}
        ],
        'watches': [
            {'name': 'ساعت مردانه', 'en_name': 'mens-watches'},
            {'name': 'ساعت زنانه', 'en_name': 'womens-watches'},
            {'name': 'ساعت هوشمند', 'en_name': 'smart-watches'}
        ],
        'glasses': [
            {'name': 'عینک آفتابی', 'en_name': 'sunglasses'},
            {'name': 'عینک طبی', 'en_name': 'eyeglasses'}
        ],
        'mobile-accessories': [
            {'name': 'قاب گوشی', 'en_name': 'phone-cases'},
            {'name': 'محافظ صفحه', 'en_name': 'screen-protectors'},
            {'name': 'شارژر و کابل', 'en_name': 'chargers-cables'}
        ]
    }
    
    created_categories = {}
    for base_cat in created_base_categories:
        created_categories[base_cat.en_name] = []
        for subcat in subcategories.get(base_cat.en_name, []):
            # ایجاد زیردسته بدون تصویر
            category = Category.objects.create(
                name=subcat['name'],
                en_name=subcat['en_name'],
                description=f"توضیحات {subcat['name']}",
                base_catgory=base_cat
            )
            
            # اضافه کردن تصویر در صورت وجود
            if use_images:
                try:
                    with open(default_img_path, 'rb') as img_file:
                        category.image.save(f"{subcat['en_name']}.png", File(img_file))
                except Exception as e:
                    print(f"خطا در اضافه کردن تصویر به زیردسته {subcat['name']}: {str(e)}")
            
            created_categories[base_cat.en_name].append(category)
            print(f"زیردسته {subcat['name']} در دسته {base_cat.name} ایجاد شد.")
    
    # ایجاد برندها
    brands_data = [
        {'name': 'سواروسکی', 'en_name': 'swarovski'},
        {'name': 'پندورا', 'en_name': 'pandora'},
        {'name': 'رومانسون', 'en_name': 'romanson'},
        {'name': 'سواچ', 'en_name': 'swatch'},
        {'name': 'ری بن', 'en_name': 'rayban'},
        {'name': 'چارمز', 'en_name': 'charms'},
        {'name': 'اپل', 'en_name': 'apple'},
        {'name': 'سامسونگ', 'en_name': 'samsung'},
        {'name': 'شیائومی', 'en_name': 'xiaomi'},
        {'name': 'اچ اند ام', 'en_name': 'hm'}
    ]
    
    created_brands = []
    for brand_data in brands_data:
        # ایجاد برند بدون لوگو
        brand = Brand.objects.create(
            name=brand_data['name'],
            en_name=brand_data['en_name'],
        )
        
        # اضافه کردن لوگو در صورت وجود
        if use_images:
            try:
                with open(default_img_path, 'rb') as img_file:
                    brand.logo.save(f"{brand_data['en_name']}.png", File(img_file))
            except Exception as e:
                print(f"خطا در اضافه کردن لوگو به برند {brand_data['name']}: {str(e)}")
        
        created_brands.append(brand)
        print(f"برند {brand_data['name']} ایجاد شد.")
    
    # برندهای ویژه
    for i, brand in enumerate(created_brands[:5]):
        FeaturedBrand.objects.create(
            brand=brand,
            active=True,
            order=i
        )
        print(f"برند ویژه {brand.name} ایجاد شد.")
    
    # ایجاد رنگ‌های پایه
    base_colors_data = [
        {'name': 'سیاه', 'color': '#000000'},
        {'name': 'سفید', 'color': '#FFFFFF'},
        {'name': 'قرمز', 'color': '#FF0000'},
        {'name': 'آبی', 'color': '#0000FF'},
        {'name': 'سبز', 'color': '#00FF00'},
        {'name': 'زرد', 'color': '#FFFF00'},
        {'name': 'نارنجی', 'color': '#FFA500'},
        {'name': 'بنفش', 'color': '#800080'},
        {'name': 'صورتی', 'color': '#FFC0CB'},
        {'name': 'طوسی', 'color': '#808080'}
    ]
    
    created_base_colors = []
    for color_data in base_colors_data:
        base_color = BaseColor.objects.create(
            name=color_data['name'],
            color=color_data['color']
        )
        created_base_colors.append(base_color)
        print(f"رنگ پایه {color_data['name']} ایجاد شد.")
    
    # ایجاد رنگ‌ها
    colors_data = [
        {'name': 'مشکی', 'hex_code': '#000000', 'base_color': 'سیاه'},
        {'name': 'سفید', 'hex_code': '#FFFFFF', 'base_color': 'سفید'},
        {'name': 'قرمز روشن', 'hex_code': '#FF0000', 'base_color': 'قرمز'},
        {'name': 'قرمز تیره', 'hex_code': '#8B0000', 'base_color': 'قرمز'},
        {'name': 'آبی روشن', 'hex_code': '#ADD8E6', 'base_color': 'آبی'},
        {'name': 'آبی تیره', 'hex_code': '#00008B', 'base_color': 'آبی'},
        {'name': 'سبز روشن', 'hex_code': '#90EE90', 'base_color': 'سبز'},
        {'name': 'سبز تیره', 'hex_code': '#006400', 'base_color': 'سبز'},
        {'name': 'زرد', 'hex_code': '#FFFF00', 'base_color': 'زرد'},
        {'name': 'نارنجی', 'hex_code': '#FFA500', 'base_color': 'نارنجی'},
        {'name': 'بنفش روشن', 'hex_code': '#E6E6FA', 'base_color': 'بنفش'},
        {'name': 'بنفش تیره', 'hex_code': '#4B0082', 'base_color': 'بنفش'},
        {'name': 'صورتی', 'hex_code': '#FFC0CB', 'base_color': 'صورتی'},
        {'name': 'طوسی روشن', 'hex_code': '#D3D3D3', 'base_color': 'طوسی'},
        {'name': 'طوسی تیره', 'hex_code': '#696969', 'base_color': 'طوسی'}
    ]
    
    created_colors = []
    for color_data in colors_data:
        base_color = next((bc for bc in created_base_colors if bc.name == color_data['base_color']), None)
        
        # ایجاد رنگ بدون تصویر
        color = Color.objects.create(
            name=color_data['name'],
            hex_code=color_data['hex_code'],
            base_color=base_color
        )
        
        # اضافه کردن تصویر در صورت وجود
        if use_images:
            try:
                with open(default_img_path, 'rb') as img_file:
                    color.image.save(f"{slugify(color_data['name'])}.png", File(img_file))
            except Exception as e:
                print(f"خطا در اضافه کردن تصویر به رنگ {color_data['name']}: {str(e)}")
        
        created_colors.append(color)
        print(f"رنگ {color_data['name']} ایجاد شد.")
    
    # ایجاد سایزها
    sizes_data = [
        {'size': 'XS', 'size_numrical': 'XXS-XS', 'category': 'clothing'},
        {'size': 'S', 'size_numrical': 'S', 'category': 'clothing'},
        {'size': 'M', 'size_numrical': 'M', 'category': 'clothing'},
        {'size': 'L', 'size_numrical': 'L', 'category': 'clothing'},
        {'size': 'XL', 'size_numrical': 'XL-XXL', 'category': 'clothing'},
        {'size': None, 'size_numrical': '36', 'category': 'shoes'},
        {'size': None, 'size_numrical': '37', 'category': 'shoes'},
        {'size': None, 'size_numrical': '38', 'category': 'shoes'},
        {'size': None, 'size_numrical': '39', 'category': 'shoes'},
        {'size': None, 'size_numrical': '40', 'category': 'shoes'},
        {'size': None, 'size_numrical': '41', 'category': 'shoes'},
        {'size': None, 'size_numrical': '42', 'category': 'shoes'},
        {'size': None, 'size_numrical': '43', 'category': 'shoes'},
        {'size': None, 'size_numrical': '44', 'category': 'shoes'},
        {'size': None, 'size_numrical': 'کوچک', 'category': 'accessories'},
        {'size': None, 'size_numrical': 'متوسط', 'category': 'accessories'},
        {'size': None, 'size_numrical': 'بزرگ', 'category': 'accessories'},
        {'size': None, 'size_numrical': 'تک سایز', 'category': 'accessories'}
    ]
    
    created_sizes = []
    for size_data in sizes_data:
        size = Size.objects.create(
            size=size_data['size'],
            size_numrical=size_data['size_numrical'],
            category=size_data['category'],
            number_size=int(size_data['size_numrical']) if size_data['size_numrical'].isdigit() else None
        )
        created_sizes.append(size)
        print(f"سایز {size_data['size'] or size_data['size_numrical']} ایجاد شد.")
    
    # ایجاد اسلایدرهای صفحه اصلی
    for i in range(3):
        # ایجاد اسلایدر بدون تصویر
        slider = HomeSlider.objects.create(
            title=f"اسلایدر {i+1}",
            subtitle=f"توضیحات اسلایدر {i+1}",
            link="#",
            active=True,
            order=i
        )
        
        # اضافه کردن تصویر در صورت وجود
        if use_images:
            try:
                with open(default_img_path, 'rb') as img_file:
                    slider.image.save(f"slider-{i+1}.png", File(img_file))
            except Exception as e:
                print(f"خطا در اضافه کردن تصویر به اسلایدر {i+1}: {str(e)}")
        
        print(f"اسلایدر {i+1} ایجاد شد.")
    
    # ایجاد بنرهای تبلیغاتی
    positions = ['top', 'middle', 'bottom']
    sizes = ['full', 'half', 'third']
    
    for pos in positions:
        for i in range(2):
            # ایجاد بنر بدون تصویر
            banner = PromotionalBanner.objects.create(
                title=f"بنر {pos} {i+1}",
                link="#",
                position=pos,
                size=random.choice(sizes),
                active=True,
                order=i
            )
            
            # اضافه کردن تصویر در صورت وجود
            if use_images:
                try:
                    with open(default_img_path, 'rb') as img_file:
                        banner.image.save(f"banner-{pos}-{i+1}.png", File(img_file))
                except Exception as e:
                    print(f"خطا در اضافه کردن تصویر به بنر {pos} {i+1}: {str(e)}")
            
            print(f"بنر {pos} {i+1} ایجاد شد.")
    
    # ایجاد محصولات
    products_data = [
        # زیورآلات - گردنبند
        {'name': 'گردنبند طلای سفید نگین دار', 'category': 'necklace', 'brand': 'swarovski', 'price': 2500000},
        {'name': 'گردنبند استیل طرح قلب', 'category': 'necklace', 'brand': 'pandora', 'price': 850000},
        {'name': 'گردنبند نقره طرح بینهایت', 'category': 'necklace', 'brand': 'charms', 'price': 1200000},
        
        # زیورآلات - دستبند
        {'name': 'دستبند چرم و استیل', 'category': 'bracelet', 'brand': 'pandora', 'price': 750000},
        {'name': 'دستبند طلا با آویز قلب', 'category': 'bracelet', 'brand': 'swarovski', 'price': 3200000},
        {'name': 'دستبند مهره‌ای رنگی', 'category': 'bracelet', 'brand': 'charms', 'price': 350000},
        
        # زیورآلات - انگشتر
        {'name': 'انگشتر نقره نگین دار', 'category': 'ring', 'brand': 'swarovski', 'price': 980000},
        {'name': 'ست حلقه ازدواج طلا سفید', 'category': 'ring', 'brand': 'pandora', 'price': 4500000},
        {'name': 'انگشتر استیل طرح تاج', 'category': 'ring', 'brand': 'charms', 'price': 450000},
        
        # زیورآلات - گوشواره
        {'name': 'گوشواره آویزی نگین دار', 'category': 'earring', 'brand': 'swarovski', 'price': 1350000},
        {'name': 'گوشواره حلقه‌ای استیل', 'category': 'earring', 'brand': 'pandora', 'price': 550000},
        {'name': 'گوشواره میخی طلا سفید', 'category': 'earring', 'brand': 'charms', 'price': 2100000},
        
        # ساعت
        {'name': 'ساعت مچی مردانه چرمی', 'category': 'mens-watches', 'brand': 'romanson', 'price': 3500000},
        {'name': 'ساعت مچی زنانه بند استیل', 'category': 'womens-watches', 'brand': 'swatch', 'price': 2800000},
        {'name': 'ساعت هوشمند اپل واچ سری 7', 'category': 'smart-watches', 'brand': 'apple', 'price': 12500000},
        {'name': 'ساعت هوشمند سامسونگ گلکسی واچ 5', 'category': 'smart-watches', 'brand': 'samsung', 'price': 8900000},
        
        # عینک
        {'name': 'عینک آفتابی ری بن مدل ویفرر', 'category': 'sunglasses', 'brand': 'rayban', 'price': 4200000},
        {'name': 'عینک آفتابی پلاریزه', 'category': 'sunglasses', 'brand': 'rayban', 'price': 3800000},
        {'name': 'عینک طبی فریم مربعی', 'category': 'eyeglasses', 'brand': 'rayban', 'price': 2700000},
        
        # اکسسوری موبایل
        {'name': 'قاب محافظ آیفون 13 پرو مکس', 'category': 'phone-cases', 'brand': 'apple', 'price': 1200000},
        {'name': 'قاب محافظ سامسونگ S22 Ultra', 'category': 'phone-cases', 'brand': 'samsung', 'price': 980000},
        {'name': 'محافظ صفحه نمایش آیفون 13', 'category': 'screen-protectors', 'brand': 'apple', 'price': 450000},
        {'name': 'شارژر وایرلس 15 وات', 'category': 'chargers-cables', 'brand': 'samsung', 'price': 1800000},
        {'name': 'کابل شارژ USB-C 100W', 'category': 'chargers-cables', 'brand': 'xiaomi', 'price': 650000}
    ]
    
    created_products = []
    for product_data in products_data:
        # پیدا کردن دسته‌بندی
        category = None
        for base_cat_name, categories in created_categories.items():
            for cat in categories:
                if cat.en_name == product_data['category']:
                    category = cat
                    break
            if category:
                break
        
        # پیدا کردن برند
        brand = next((b for b in created_brands if b.en_name == product_data['brand']), None)
        
        if not category or not brand:
            print(f"خطا در پیدا کردن دسته‌بندی یا برند برای محصول {product_data['name']}")
            continue
        
        # ایجاد محصول بدون تصویر
        product = Product.objects.create(
            name=product_data['name'],
            description=fake.paragraph(nb_sentences=5),
            is_active=True
        )
        
        # اضافه کردن تصویر در صورت وجود
        if use_images:
            try:
                with open(default_img_path, 'rb') as img_file:
                    product.image.save(f"{slugify(product_data['name'])}.png", File(img_file))
            except Exception as e:
                print(f"خطا در اضافه کردن تصویر به محصول {product_data['name']}: {str(e)}")
        
        # اضافه کردن دسته‌بندی‌ها
        product.categories.add(category)
        
        created_products.append(product)
        print(f"محصول {product_data['name']} ایجاد شد.")
        
        # ایجاد گالری تصاویر برای محصول
        if use_images:
            for i in range(random.randint(2, 4)):
                try:
                    gallery = Gallery.objects.create(product=product)
                    with open(default_img_path, 'rb') as img_file:
                        gallery.image.save(f"{slugify(product_data['name'])}-gallery-{i+1}.png", File(img_file))
                    print(f"تصویر {i+1} برای گالری محصول {product_data['name']} اضافه شد.")
                except Exception as e:
                    print(f"خطا در اضافه کردن تصویر به گالری محصول {product_data['name']}: {str(e)}")
        
        # ایجاد بسته‌های محصول با رنگ‌ها و سایزهای مختلف
        for color in random.sample(created_colors, random.randint(2, 4)):
            for size in random.sample(created_sizes, random.randint(1, 3)):
                # محاسبه قیمت با تنوع کوچک
                base_price = product_data['price']
                variation = random.uniform(0.95, 1.05)
                price = int(base_price * variation)
                
                # تخفیف برای برخی محصولات
                discount = 0
                is_active_discount = False
                if random.random() < 0.3:  # 30% احتمال تخفیف
                    discount = random.randint(5, 30)
                    is_active_discount = True
                
                package = ProductPackage.objects.create(
                    product=product,
                    size=size,
                    brand=brand,
                    color=color,
                    quantity=random.randint(5, 50),
                    weight=random.randint(100, 500),
                    is_active_package=True,
                    price=price,
                    discount=discount,
                    is_active_discount=is_active_discount,
                    sold_count=random.randint(0, 20),
                    views_count=random.randint(10, 100),
                    rating=round(random.uniform(3.0, 5.0), 1)
                )
                
                print(f"بسته محصول برای {product_data['name']} با رنگ {color.name} و سایز {size.size or size.size_numrical} ایجاد شد.")
    
    print("ایجاد داده‌های نمایشی با موفقیت به پایان رسید.")
    return True

if __name__ == "__main__":
    create_demo_data() 