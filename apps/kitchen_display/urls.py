from django.urls import path
from . import views

urlpatterns = [
    path('display/', views.KitchenOrderListView.as_view(), name="kitchen-board"),
]
