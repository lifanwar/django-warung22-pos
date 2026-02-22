# point_off_sale/admin.py
from django.contrib import admin
from .models import (
    UserProfile,
    Table,
    MenuCategory,
    MenuGroup,
    MenuItem,
    Order,
    OrderItem,
)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "role")
    list_filter = ("role",)
    search_fields = ("user__username", "user__first_name", "user__last_name")

@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = ("number", "capacity", "is_active")
    list_filter = ("is_active",)
    search_fields = ("number",)

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

    def get_category(self, obj):
        return obj.category.name
    get_category.short_description = "Category"

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("created_at", "updated_at")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "customer_name", "table", "guest_count", "order_type", "status", "created_at")
    list_filter = ("status", "order_type", "created_at")
    search_fields = ("name", "table__number")
    inlines = [OrderItemInline]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = (
        "order",
        "menu_item",
        "quantity",
        "status",
        "get_prep_station",
        "created_at",
        "updated_at",
        "updated_by",
    )
    list_filter = ("status", "menu_item__prep_station", "created_at")
    search_fields = ("order__id", "menu_item__name")

    def get_prep_station(self, obj):
        return obj.menu_item.prep_station
    get_prep_station.short_description = "Prep station"
