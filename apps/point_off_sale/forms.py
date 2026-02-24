from django import forms
from decimal import Decimal
from django.contrib import messages
from . import models
import json


class OrderDirectSalesForm(forms.Form):
    cart_payload = forms.CharField(widget=forms.HiddenInput)

    def process_order(self, request):
        cart_payload = self.cleaned_data["cart_payload"]

        try:
            cart_data = json.loads(cart_payload)
        except json.JSONDecodeError:
            return None

        cart_items = []
        for item in cart_data:
            try:
                menu_id = int(item.get("id"))
                qty = int(item.get("quantity", 0))
            except (TypeError, ValueError):
                continue
            if menu_id and qty > 0:
                cart_items.append({"id": menu_id, "quantity": qty})

        if not cart_items:
            return None

        # Get menu just 1 query
        menu_ids = [item["id"] for item in cart_items]
        menus = models.MenuItem.objects.filter(
            id__in=menu_ids,
            is_available=True,
        )
        menu_map = {m.id: m for m in menus}

        # 3) Make an Order
        order = models.Order.objects.create(
            customer_name="Direct Sales",
            table=None,
            guest_count=1,
            order_type="dine_in",
            status="closed",
        )

        # 4) Calculate subtotal + bulk_create items
        subtotal = Decimal("0.00")
        order_items_to_create = []

        updated_by = request.user if request.user.is_authenticated else None

        for item in cart_items:
            menu = menu_map.get(item["id"])
            if not menu:
                continue

            qty = item["quantity"]
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
                    updated_by=updated_by,
                )
            )

        if order_items_to_create:
            models.OrderItem.objects.bulk_create(order_items_to_create)

        # 5) Update subtotal
        order.subtotal = subtotal
        order.save(update_fields=["subtotal"])

        messages.success(request, "Payment berhasil disimpan.")
        return order
