from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.edit import FormView
from django.views.generic import ListView, DetailView
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
        context = super().get_context_data(**kwargs)
        context["menu"] = self.get_menu_queryset()
        context["categories"] = models.MenuCategory.objects.order_by("name")
        return context

    def form_valid(self, form):
        button_type = self.request.POST.get("button_type")

        if button_type == "direct_payment":
            order = form.process_direct_sales_order(self.request)
            if not order:
                return redirect("point-off-sales")
        return super().form_valid(form)

class OrderList(ListView):
    model = models.Order
    template_name = "point_off_sale/order_list.html"
    context_object_name = 'orders'
    ordering = ['-created_at']

    VALID_TYPES = ['dine_in', 'takeaway', 'delivery']
    VALID_STATUS = ['active', 'pending', 'closed']

    def get_queryset(self):
        qs = models.Order.objects.only(
            'id',
            'customer_name',
            'table',
            'order_type',
            'status',
            'subtotal',
            'created_at'
        ).select_related('table').order_by('-created_at')

        order_type = self.request.GET.get('type')      
        status = self.request.GET.get('status')   

        if order_type in self.VALID_TYPES:
            qs = qs.filter(order_type=order_type)

        if status in self.VALID_STATUS:
            qs = qs.filter(status=status)

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_type'] = self.request.GET.get('type', '')
        context['active_status'] = self.request.GET.get('status', '')
        return context

@method_decorator(csrf_exempt, name='dispatch')
class OrderDetailAjaxView(DetailView):
    model = models.Order
    template_name = "point_off_sale/snippets/order_list/right-panel.html"
    
    def post(self, request, *args, **kwargs):
        if request.POST.get('action') == 'delete':
            self.get_object().delete()
            return redirect('orderlist') 
        return self.get(request, *args, **kwargs)
    