from django.urls import path

from .views import (
    cliente_crear,
    cliente_detalle,
    cliente_editar,
    cliente_eliminar,
    cliente_listar,
)

app_name = "clientes"

urlpatterns = [
    path("", cliente_listar, name="listar"),
    path("nuevo/", cliente_crear, name="crear"),
    path("<int:cliente_id>/", cliente_detalle, name="detalle"),
    path("<int:cliente_id>/editar/", cliente_editar, name="editar"),
    path("<int:cliente_id>/eliminar/", cliente_eliminar, name="eliminar"),
]
