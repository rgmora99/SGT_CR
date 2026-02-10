from django.contrib import admin
from .models import Contrato, ContratoDocumento


@admin.register(Contrato)
class ContratoAdmin(admin.ModelAdmin):
    list_display = ("numero", "contratista", "gerencia", "monto", "tipo", "estado", "fecha_inicio", "fecha_fin")
    search_fields = ("numero", "contratista", "gerencia")
    list_filter = ("tipo", "estado", "gerencia")
    ordering = ("-created_at",)


@admin.register(ContratoDocumento)
class ContratoDocumentoAdmin(admin.ModelAdmin):
    list_display = ("contrato", "nombre", "subido_en")
    search_fields = ("contrato__numero", "nombre")
    ordering = ("-subido_en",)