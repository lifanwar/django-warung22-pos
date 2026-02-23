from django.urls import path
from . import views

urlpatterns = [
    path('', views.CreateOrder.as_view(), name='point-off-sales')
]
