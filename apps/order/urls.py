from django.urls import path
from . import views

urlpatterns = [
    path('pos/', views.CreateOrderView.as_view(), name='point-off-sales'),
    path('orders/', views.OrderList.as_view(), name='orderlist'),
    path('orders/<int:pk>/', views.OrderDetailAjaxView.as_view(), name='order-detail'),
]
