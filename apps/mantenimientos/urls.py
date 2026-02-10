
from django.urls import path
from .views import *

app_name = "contratos"

urlpatterns = [
    path("", listar_contratos, name="listar"),
    path("nuevo/", crear_contrato, name="crear"),
    path("<int:contrato_id>/", contrato_ver, name="ver"),

    path("<int:contrato_id>/documentos/", subir_documento, name="documento"),

    path("<int:contrato_id>/prorrogas/", listar_prorrogas, name="prorrogas"),
    path("<int:contrato_id>/prorrogas/nueva/", crear_prorroga, name="crear_prorroga"),

    path("<int:contrato_id>/ordenes/", listar_ordenes, name="ordenes"),
    path("<int:contrato_id>/ordenes/nueva/", crear_orden, name="crear_orden"),

    path("<int:contrato_id>/garantias/", listar_garantias, name="garantias"),
    path("<int:contrato_id>/garantias/nueva/", crear_garantia, name="crear_garantia"),

    path("<int:contrato_id>/seguimiento/", seguimiento_contrato, name="seguimiento"),
]
