# apps/billing/services.py
from decimal import Decimal
from .models import Invoice, InvoiceItem, Payment

def generate_invoice_number():
    from uuid import uuid4
    return f"INV-{uuid4().hex[:8].upper()}"

class InvoiceServices:

    @staticmethod
    def create_for_order(order) -> Invoice:
        invoice = Invoice.objects.create(
            order=order,
            number=generate_invoice_number(),
            status='open',  # nanti langsung di-set paid setelah payment
        )
        items = []
        for order_item in order.items.all():
            items.append(
                InvoiceItem(
                    invoice=invoice,
                    order_item=order_item,
                    quantity=order_item.quantity,
                    unit_price=order_item.menu_item.price,
                )
            )
        InvoiceItem.objects.bulk_create(items)
        invoice.recalc_total()
        return invoice


class PaymentServices:

    @staticmethod
    def add_full_payment(invoice: Invoice, method: str = 'cash') -> Payment:
        amount = invoice.total or Decimal("0.00")
        payment = Payment.objects.create(
            invoice=invoice,
            amount=amount,
            method=method,
        )

        # Invoice pasti lunas
        invoice.status = 'paid'
        invoice.save(update_fields=['status'])

        # Order direct sales pasti closed
        order = invoice.order
        order.status = 'closed'
        order.save(update_fields=['status'])

        return payment

