from django import forms
from decimal import Decimal
from django.contrib import messages
from . import models
import json


class OrderDirectSalesForm(forms.Form):
    cart_payload = forms.CharField(widget=forms.HiddenInput)

    def process_order(self, request):
        cart_payload = self.cleaned_data["cart_payload"]
        print(cart_payload)

        try:
            cart_data = json.loads(cart_payload)
        except json.JSONDecodeError:
            return None

        cart_items = [
            item for item in cart_data
            if item.get("id") and int(item.get("quantity", 0)) > 0
        ]
        if not cart_items:
            return None

        menu_ids = [item["id"] for item in cart_items]
        menu_qs = models.MenuItem.objects.filter(
            id__in=menu_ids, is_available=True
        )
        menu_map = {str(m.id): m for m in menu_qs}

        order = models.Order.objects.create(
            customer_name="Direct Sales",
            table=None,
            guest_count=1,
            order_type="dine_in",
            status="closed",
        )

        subtotal = Decimal("0.00")
        order_items_to_create = []

        for item in cart_items:
            menu = menu_map.get(str(item["id"]))
            if not menu:
                continue

            qty = int(item["quantity"])
            if qty <= 0:
                continue

            line_total = menu.price * qty
            subtotal += line_total

            order_items_to_create.append(
                models.OrderItem(
                    order=order,
                    menu_item=menu,
                    quantity=qty,
                    notes="",
                    status="done",
                    updated_by=request.user if request.user.is_authenticated else None,
                )
            )

        if order_items_to_create:
            models.OrderItem.objects.bulk_create(order_items_to_create)

        order.subtotal = subtotal
        order.save(update_fields=["subtotal"])

        messages.success(request, "Payment berhasil disimpan.")
        return order
