from django.urls import path

from . import views

app_name = "ventas"

urlpatterns = [
    path("", views.listar_venta, name="listar"),
    path("nuevo/", views.crear_venta, name="crear"),
    path("inventario/", views.inventario_dashboard, name="inventario"),
    path("inventario/productos/", views.listar_productos, name="productos"),
    path("inventario/productos/nuevo/", views.crear_producto, name="producto_crear"),
    path("inventario/productos/<int:producto_id>/editar/", views.editar_producto, name="producto_editar"),
    path("inventario/catalogos/", views.mantenimiento_catalogos, name="catalogos"),
]
