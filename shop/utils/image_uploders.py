import os 
from django.utils.crypto import get_random_string

# image handling
def get_filename_ext(filepath):
    base_name = os.path.basename(filepath)
    name, ext = os.path.splitext(base_name)
    return name, ext

def upload_image_path(instance, filename):
    name, ext = get_filename_ext(filename)
    unique_id = get_random_string(length=15)
    final_name = f"image-{unique_id}{ext}"
    return f"product-images/{final_name}"

def upload_color_image_path(instance, filename):
    name, ext = get_filename_ext(filename)
    unique_id = get_random_string(length=15)
    final_name = f"image-{unique_id}{ext}"
    return f"color-images/{final_name}"

def upload_cat_image_path(instance, filename):
    name, ext = get_filename_ext(filename)
    unique_id = get_random_string(length=15)
    final_name = f"image-{unique_id}{ext}"
    return f"categories/{final_name}"

def upload_brand_image_path(instance, filename):
    name, ext = get_filename_ext(filename)
    unique_id = get_random_string(length=15)
    final_name = f"image-{unique_id}{ext}"
    return f"brands/{final_name}"
    
def upload_BaseCategory_image_path(instance, filename):
    name, ext = get_filename_ext(filename)
    unique_id = get_random_string(length=15)
    final_name = f"image-{unique_id}{ext}"
    return f"color-images/{final_name}"  # change directory name

# مدل جدید برای اسلایدرهای صفحه اصلی
def upload_slider_image_path(instance, filename):
    name, ext = get_filename_ext(filename)
    unique_id = get_random_string(length=15)
    final_name = f"slider-{unique_id}{ext}"
    return f"slider-images/{final_name}"


# مدل جدید برای بنرهای تبلیغاتی
def upload_banner_image_path(instance, filename):
    name, ext = get_filename_ext(filename)
    unique_id = get_random_string(length=15)
    final_name = f"banner-{unique_id}{ext}"
    return f"banner-images/{final_name}"

