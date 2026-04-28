from datetime import datetime
from shop.sitesettings.models import SiteSettings, StaticPage
from shop.categories.models import Category, BaseCategories

def site_settings(request):
    """
    Context processor برای دسترسی به تنظیمات سایت در تمام قالب‌ها
    """
    try:
        # دریافت اولین مورد از تنظیمات سایت (معمولاً فقط یک مورد وجود دارد)
        settings = SiteSettings.objects.first()
    except:
        settings = None
    
    # دریافت صفحات استاتیک فعال
    try:
        pages = StaticPage.objects.filter(active=True)
    except:
        pages = []
    
    # سال جاری برای نمایش در فوتر
    current_year = datetime.now().year
    
    return {
        'site_settings': settings,
        'static_pages': pages,
        'current_year': current_year,
    }

def categories(request):
    """
    Context processor to include categories in all templates
    """
    return {
        'all_categories': Category.objects.filter(parent=None),  # فقط دسته‌بندی‌های اصلی
        'all_categories_list': Category.objects.all(),  # همه دسته‌بندی‌ها
        'base_categories': BaseCategories.objects.all()  # دسته‌بندی‌های پایه
    } 