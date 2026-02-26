from django.db import models
from apps.point_off_sale.models import Order, OrderItem

# Create your models here.

class Invoice(models.Model):
    STATUS = [
        ('open', 'Open'),
        ('partial', 'Partial'),
        ('paid', 'Paid'),
        ('cancel', 'Cancel'),
    ]
    order      = models.ForeignKey(Order, on_delete=models.PROTECT, related_name='invoices')
    number     = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status     = models.CharField(max_length=20, choices=STATUS, default='open')
    total      = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def recalc_total(self):
        self.total = sum(item.line_total for item in self.items.all())
        self.save(update_fields=['total'])

    @property
    def paid_amount(self):
        return sum(p.amount for p in self.payments.all())

    @property
    def balance(self):
        return self.total - self.paid_amount

    def __str__(self):
        return f"Invoice {self.number} for Order #{self.order_id}"


class InvoiceItem(models.Model):
    invoice    = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='items')
    order_item = models.ForeignKey(OrderItem, on_delete=models.PROTECT, related_name='invoice_items')
    quantity   = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2) # Get from OrderItem.menu_item.price for consistency

    @property
    def line_total(self):
        if self.unit_price is None or self.quantity is None:
            return 0
        return self.unit_price * self.quantity

    def __str__(self):
        return f"{self.quantity}x {self.order_item.menu_item.name} on {self.invoice}"


class Payment(models.Model):
    METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('transfer', 'Transfer'),
    ]
    invoice = models.ForeignKey(Invoice, on_delete=models.PROTECT, related_name='payments')
    amount  = models.DecimalField(max_digits=10, decimal_places=2)
    method  = models.CharField(max_length=20, choices=METHOD_CHOICES)
    paid_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.amount} for {self.invoice}"