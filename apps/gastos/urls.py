from django.urls import path
from apps.gastos.views.acciones import aprobar_factura, rechazar_factura
from apps.gastos.views.correo_config import  config_correo_facturas 
from apps.gastos.views.bandeja import bandeja_facturas
from django.urls import path
from apps.gastos.views.sync import sync_facturas_ajax

app_name = "gastos"

urlpatterns = [
    path("config-correo-facturas/", config_correo_facturas, name="config_correo_facturas"),
    path("bandeja-facturas/", bandeja_facturas, name="bandeja_facturas"),
    path("facturas/<int:factura_id>/aprobar/", aprobar_factura, name="aprobar_factura"),
    path("facturas/<int:factura_id>/rechazar/", rechazar_factura, name="rechazar_factura"),
    path("sync-facturas/", sync_facturas_ajax, name="sync_facturas_ajax"),
]