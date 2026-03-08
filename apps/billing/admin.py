from django.contrib import admin
from .models import Invoice, InvoiceItem, Payment


class InvoiceItemInline(admin.TabularInline):  # atau admin.StackedInline
    model = InvoiceItem
    extra = 1  # jumlah form kosong tambahan


class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 1


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('number', 'order', 'status', 'total', 'paid_amount', 'balance', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('number', 'order__id')
    inlines = [InvoiceItemInline, PaymentInline]


@admin.register(InvoiceItem)
class InvoiceItemAdmin(admin.ModelAdmin):
    list_display = ('invoice', 'order_item', 'quantity', 'unit_price', 'line_total')
    search_fields = ('invoice__number', 'order_item__menu_item__name')


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('invoice', 'amount', 'method', 'paid_at')
    list_filter = ('method', 'paid_at')
    search_fields = ('invoice__number',)

