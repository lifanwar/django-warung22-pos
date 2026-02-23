from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from apps.point_off_sale.models import Order, OrderItem
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect

class StationOrder(LoginRequiredMixin, ListView):
    login_url = '/admin/login/'  # Optional: specify your login URL
    redirect_field_name = 'next'  
    model = Order
    template_name = "kitchen_display/displaykitchen.html"
    context_object_name = "orders"

    prep_station = None  # 'kitchen' atau 'bar'

    def get_prep_station(self):
        """
        Map role user ke prep_station.
        chef / assistant_chef -> 'kitchen'
        bartender -> 'bar'
        """
        profile = getattr(self.request.user, "userprofile", None)
        if profile is None:
            # default aman, terserah kamu mau apa
            return "kitchen"

        if profile.role in ("chef", "assistant_chef"):
            return "kitchen"
        elif profile.role == "bartender":
            return "bar"
        return "kitchen"

    def get_status_filter(self):
        status = self.request.GET.get("status", "all")
        if status not in ("all", "to_cook", "ready", "completed"):
            status = "all"
        return status

    def get_queryset(self):
        prep_station = self.get_prep_station()

        if prep_station is None:
            raise ValueError("prep_station harus di-set di subclass")

        status_filter = self.get_status_filter()

        qs = (
            Order.objects
            .filter(status="open")
            .prefetch_related(
                "items",
                "items__menu_item",
                "items__menu_item__group",
            )
            .select_related("table")
        )

        # hanya order yang punya item untuk station ini + status tersebut
        filtered_orders = []
        for o in qs:
            items = o.items.filter(menu_item__prep_station=prep_station)
            if status_filter != "all":
                items = items.filter(status=status_filter)
            else:
                items = items.exclude(status="done")
            if items.exists():
                filtered_orders.append(o)

        return filtered_orders
    
    def post(self, request, *args, **kwargs):
        action = request.POST.get("action")
        order_id = request.POST.get("order_id")

        # Number Validation
        try:
            order_id = int(order_id)
            if order_id <= 0:
                raise ValueError
        except (TypeError, ValueError):
            return HttpResponseBadRequest("Invalid order_id")

        if action not in ("reset_to_cook", "complete_order"):
            return HttpResponseBadRequest("Invalid action")

        order = get_object_or_404(Order, pk=order_id, status="open")

        prep_station = self.get_prep_station()

        qs = OrderItem.objects.filter(
            order=order,
            menu_item__prep_station=prep_station,
        )

        if action == "reset_to_cook":
            qs.filter(status="completed").update(status="to_cook")
        elif action == "complete_order":
            qs.filter(status="completed").update(status="done")

        return redirect(request.path + "?" + request.META.get("QUERY_STRING", ""))

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["station"] =  self.get_prep_station()
        ctx["status_filter"] = self.get_status_filter()
        return ctx