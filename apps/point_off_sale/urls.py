from django.urls import path
from . import views

urlpatterns = [
    path('', views.CreateOrderView.as_view(), name='point-off-sales')
]
