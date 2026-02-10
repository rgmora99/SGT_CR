from django.urls import path
from . import views

app_name = "ventas"

urlpatterns = [
    path("", views.listar_venta, name="listar"),
    path("nuevo/", views.crear_venta, name="crear"),  
]
