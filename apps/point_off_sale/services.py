from decimal import Decimal
import json
from typing import Optional

from django.contrib import messages
from django.db import transaction
from django.http import HttpRequest

from . import models


class OrderServices:

    @staticmethod
    def order_direct_sales(
        request: HttpRequest,
        cart_payload: str,
        order_type: str = None,
    ) -> Optional[models.Order]:
        """
        Membuat order direct sales dari cart payload JSON.
        Mengembalikan Order jika berhasil, None jika validasi gagal.
        """
        try:
            with transaction.atomic():
                cart_items = OrderServices._parse_cart(request, cart_payload)
                menu_map = OrderServices._validate_menu_availability(request, cart_items)
                order = OrderServices._create_order(order_type)
                OrderServices._populate_order_items(request, order, cart_items, menu_map)

        except ValueError:
            return None

        messages.success(request, "Payment berhasil disimpan.")
        return order

    # ------------------------------------------------------------------ #
    #  Private Helpers                                                     #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _parse_cart(request: HttpRequest, cart_payload: str) -> list[dict]:
        """Parse JSON payload dan normalisasi menjadi list {id, quantity}."""
        try:
            cart_data = json.loads(cart_payload)
        except json.JSONDecodeError:
            messages.error(request, "Keranjang tidak valid, silakan coba lagi.")
            raise ValueError("invalid_cart")

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
            messages.error(request, "Keranjang kosong atau tidak valid.")
            raise ValueError("empty_cart")

        return cart_items

    @staticmethod
    def _validate_menu_availability(
        request: HttpRequest,
        cart_items: list[dict],
    ) -> dict[int, models.MenuItem]:
        """
        Validasi semua menu di cart tersedia.
        Mengembalikan dict {menu_id: MenuItem} jika valid.
        """
        menu_ids = [item["id"] for item in cart_items]

        menus = models.MenuItem.objects.filter(id__in=menu_ids)
        menu_map = {m.id: m for m in menus}

        unavailable = [m for m in menu_map.values() if not m.is_available]
        if unavailable:
            nama_menu = ", ".join(m.name for m in unavailable)
            messages.error(
                request,
                f"Menu berikut sudah habis/tidak tersedia:\n{nama_menu}"
            )
            raise ValueError("menu_not_available")

        return menu_map


    @staticmethod
    def _create_order(order_type: str) -> models.Order:
        """Membuat record Order baru."""
        return models.Order.objects.create(
            customer_name="Direct Sales",
            table=None,
            guest_count=1,
            order_type=order_type,
            status="closed",
        )

    @staticmethod
    def _populate_order_items(
        request: HttpRequest,
        order: models.Order,
        cart_items: list[dict],
        menu_map: dict[int, models.MenuItem],
    ) -> None:
        """Buat OrderItem secara bulk dan update subtotal order."""
        updated_by = request.user if request.user.is_authenticated else None
        subtotal = Decimal("0.00")
        order_items = []

        for item in cart_items:
            menu = menu_map[item["id"]]
            qty = item["quantity"]
            subtotal += menu.price * qty
            order_items.append(
                models.OrderItem(
                    order=order,
                    menu_item=menu,
                    quantity=qty,
                    notes="",
                    status="done",
                    updated_by=updated_by,
                )
            )

        if not order_items:
            messages.error(request, "Tidak ada item yang bisa disimpan.")
            raise ValueError("no_order_items")

        models.OrderItem.objects.bulk_create(order_items)
        order.subtotal = subtotal
        order.save(update_fields=["subtotal"])
