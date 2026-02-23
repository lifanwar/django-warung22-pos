from django.views.generic import ListView
from . import models

# Create your views here.
class CreateOrder(ListView):
    template_name = 'point_off_sale/index.html'
    context_object_name = 'menu'

    def get_queryset(self):

        qs = models.MenuItem.objects.filter(
            is_available=True,
         ).select_related(
            "group", "group__category"
         ).order_by(
            "group__category__name", "group__name", "name"
         )
        
        category_slug = self.request.GET.get("category")
        if category_slug:
            qs = qs.filter(group__category__name__iexact=category_slug)

        return qs
    

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        # daftar kategori untuk tab
        ctx["categories"] = models.MenuCategory.objects.order_by("name")

        # kategori aktif untuk highlight tab
        ctx["active_category"] = self.request.GET.get("category") or "all"

        return ctx
        
