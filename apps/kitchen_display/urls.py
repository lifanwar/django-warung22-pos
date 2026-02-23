from django.urls import path
from . import views

app_name = 'kitchen_display'

urlpatterns = [
    path("kitchen/", views.StationOrder.as_view(), name="kitchen-display"),
]
