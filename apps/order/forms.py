from django import forms
from .services import OrderServices


class OrderDirectSalesForm(forms.Form):
    cart_payload = forms.CharField(widget=forms.HiddenInput)
    order_type = forms.CharField(widget=forms.HiddenInput, required=False)

    def process_direct_sales_order(self, request):
        return OrderServices.order_direct_sales(
            request=request,
            cart_payload=self.cleaned_data["cart_payload"],
            order_type=self.cleaned_data.get("order_type"),
        )
