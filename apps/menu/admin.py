from django.contrib import admin
from .models import MenuCategory, MenuGroup, MenuItem

# Register your models here.

@admin.register(MenuCategory)
class MenuCategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(MenuGroup)
class MenuGroupAdmin(admin.ModelAdmin):
    list_display = ("name", "category")
    list_filter = ("category",)
    search_fields = ("name", "category__name")


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ("name", "group", "get_category", "price", "prep_station", "is_available")
    list_filter = ("prep_station", "is_available", "group__category")
    search_fields = ("name", "group__name", "group__category__name")
    list_editable = ("is_available",)

    def get_category(self, obj):
        return obj.category.name
    get_category.short_description = "Category"