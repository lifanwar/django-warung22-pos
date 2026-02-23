from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

urlpatterns = [
    path('display/', views.KitchenOrderListView.as_view(), name="kitchen-board"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
]
