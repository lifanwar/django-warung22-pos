from django.views.generic.edit import FormView
from django.urls import reverse_lazy
from django.shortcuts import redirect
from . import models
from .forms import OrderDirectSalesForm
        
class CreateOrderView(FormView):
    template_name = "point_off_sale/index.html"
    form_class = OrderDirectSalesForm
    success_url = reverse_lazy("point-off-sales")

    def get_menu_queryset(self):
        return (
            models.MenuItem.objects.filter(is_available=True)
            .select_related("group", "group__category")
            .order_by("group__category__name", "group__name", "name")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)  # penting supaya form masuk context [web:17]
        context["menu"] = self.get_menu_queryset()
        context["categories"] = models.MenuCategory.objects.order_by("name")
        return context

    def form_valid(self, form):
        order = form.process_order(self.request)
        if not order:
            return redirect("point-off-sales")
        return super().form_valid(form)