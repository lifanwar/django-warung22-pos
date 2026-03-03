from django.contrib import admin
from django.urls import path, include
from apps.core import views as coreView
from django.contrib.auth import views as auth_views

AUTH = [
    path('admin/', admin.site.urls),
    path('login/', coreView.login.as_view(), name='login'),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
]

APPS = [
    path('display/', include('apps.kitchen_display.urls')),
    path('order/', include('apps.order.urls'))
]

urlpatterns = AUTH + APPS