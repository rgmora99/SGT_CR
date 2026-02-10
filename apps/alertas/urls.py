from django.urls import path
from . import views

app_name = "alertas"

urlpatterns = [
    path("", views.listar_alertas, name="listar"),
    path("nuevo/", views.crear_alerta, name="crear"),  
    path("<int:id>/", views.ver_alerta , name="ver"),
    path("<int:pk>/atender/", views.marcar_atendida, name="atender"),
    path("<int:pk>/eliminar/", views.eliminar_alerta, name="eliminar"),
]
