from django.contrib import admin
from django.contrib import admin
from shop.categories.models import *
from mptt.admin import DraggableMPTTAdmin



# Register your models here.
@admin.register(Category)
class CategoryAdmin(DraggableMPTTAdmin):
    mptt_indent_field = "name"
    list_display = ('tree_actions', 'indented_title', 'parent', 'description',)
    list_display_links = ('indented_title',)
    search_fields = ['name', 'description']
    list_filter = ['parent']
    filter_horizontal = ['brand']
