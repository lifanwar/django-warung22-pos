from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

urlpatterns = [
    path("display/", views.StationOrder.as_view(), name="kitchen-display"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
]
