from decimal import Decimal
import json
from django.contrib import messages
from django.db import transaction
from . import models


class CartValidationError(Exception):
    """Error khusus untuk validasi cart."""


class OrderServices:

    @staticmethod
    def order_direct_sales(request, cart_payload: str, order_type: str = None):
        try:
            with transaction.atomic():
                # 1) Parse JSON payload
                try:
                    cart_data = json.loads(cart_payload)
                except json.JSONDecodeError:
                    messages.error(request, "Keranjang tidak valid, silakan coba lagi.")
                    raise CartValidationError("invalid_cart")

                # 2) Normalisasi cart -> list id & qty
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
                    raise CartValidationError("empty_cart")

                menu_ids = [i["id"] for i in cart_items]

                # 3) Validasi: semua id di cart harus tersedia
                menus = list(
                    models.MenuItem.objects.filter(
                        id__in=menu_ids,
                        is_available=True,
                    )
                )
                available_ids = {m.id for m in menus}

                missing_ids = set(menu_ids) - available_ids
                if missing_ids:
                    # Ada menu di cart yang tidak tersedia / tidak ditemukan
                    messages.error(
                        request,
                        "Beberapa menu di keranjang tidak tersedia lagi. "
                        "Silakan periksa keranjang Anda.",
                    )
                    raise CartValidationError("menu_not_available")

                # Kalau sampai sini, berarti SEMUA menu di cart valid & available
                menu_map = {m.id: m for m in menus}

                # 4) Buat Order
                order = models.Order.objects.create(
                    customer_name="Direct Sales",
                    table=None,
                    guest_count=1,
                    order_type=order_type,
                    status="closed",
                )

                # 5) Hitung subtotal & siapkan OrderItem
                subtotal = Decimal("0.00")
                order_items_to_create = []
                updated_by = request.user if request.user.is_authenticated else None

                for item in cart_items:
                    menu = menu_map[item["id"]]  # aman, sudah divalidasi
                    qty = item["quantity"]

                    subtotal += menu.price * qty
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

                if not order_items_to_create:
                    messages.error(request, "Tidak ada item yang bisa disimpan.")
                    raise CartValidationError("no_order_items")

                models.OrderItem.objects.bulk_create(order_items_to_create)

                order.subtotal = subtotal
                order.save(update_fields=["subtotal"])

        except CartValidationError:
            return None

        messages.success(request, "Payment berhasil disimpan.")
        return order
