from django.views.generic import ListView, View
from . import models
import json
from decimal import Decimal
from django.shortcuts import render, redirect
from django.contrib import messages

# Create your views here.
class CreateOrder(ListView):
    template_name = 'point_off_sale/index.html'
    context_object_name = 'menu'

    def get_queryset(self):
        return (
            models.MenuItem.objects.filter(is_available=True)
            .select_related("group", "group__category")
            .order_by("group__category__name", "group__name", "name")
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["categories"] = models.MenuCategory.objects.order_by("name")
        # active_category tidak perlu lagi, semua dihandle JS
        return ctx

        
class CreateOrderView(View):
    template_name = 'point_off_sale/index.html'

    def get_menu_queryset(self):
        return (
            models.MenuItem.objects.filter(is_available=True)
            .select_related("group", "group__category")
            .order_by("group__category__name", "group__name", "name")
        )

    def get_context_data(self, **kwargs):
        ctx = {
            "menu": self.get_menu_queryset(),
            "categories": models.MenuCategory.objects.order_by("name"),
        }
        ctx.update(kwargs)
        return ctx

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        cart_payload = request.POST.get("cart_payload", "")
        if not cart_payload:
            return redirect("point-off-sales")

        try:
            cart_data = json.loads(cart_payload)
        except json.JSONDecodeError:
            return redirect("point-off-sales")

        cart_items = [
            item for item in cart_data
            if item.get("id") and int(item.get("quantity", 0)) > 0
        ]
        if not cart_items:
            return redirect("point-off-sales")

        menu_ids = [item["id"] for item in cart_items]
        menu_qs = models.MenuItem.objects.filter(id__in=menu_ids, is_available=True)
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

        return redirect("point-off-sales")