from django.views.generic import ListView
from . import models

# Create your views here.
class CreateOrder(ListView):
    template_name = 'point_off_sale/index.html'
    context_object_name = 'menu'

    def get_queryset(self):

        menu = models.MenuItem.objects.filter(
            is_available=True,
        ).select_related(
            "group", "group__category"
            ).order_by(
                "group__category__name", "group__name", "name"
                )
        
        return menu
