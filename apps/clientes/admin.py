from django.contrib import admin

from .models import Cliente, TipoIdentificacion


@admin.register(TipoIdentificacion)
class TipoIdentificacionAdmin(admin.ModelAdmin):
    list_display = ("nombre", "codigo", "ejemplo", "activo", "orden")
    search_fields = ("nombre", "codigo")
    list_filter = ("activo",)


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = (
        "nombre",
        "tipo_identificacion",
        "identificacion",
        "correo_electronico",
        "telefono",
        "estado",
        "actualizado_en",
    )
    search_fields = ("nombre", "identificacion", "correo_electronico", "telefono")
    list_filter = ("estado", "tipo_identificacion")
