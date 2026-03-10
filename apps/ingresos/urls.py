from django.urls import path

from . import views

app_name = "ingresos"

urlpatterns = [
    path("", views.listado_ingresos, name="listado"),
    path("nuevo/", views.crear_ingreso, name="crear"),
    path("<int:ingreso_id>/", views.ver_ingreso, name="ver_ingreso"),
    path("<int:ingreso_id>/editar/", views.editar_ingreso, name="editar"),
    path("<int:ingreso_id>/anular/", views.anular_ingreso, name="anular"),
    path("api/tipo-cambio/", views.tipo_cambio_bcr, name="tipo_cambio_bcr"),
]
