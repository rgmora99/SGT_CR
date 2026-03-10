from django.contrib import admin
from .models import CategoriaGasto, ProveedorGasto

@admin.register(CategoriaGasto)
class CategoriaGastoAdmin(admin.ModelAdmin):
    list_display = ("id", "negocio", "nombre", "activo")
    list_filter = ("negocio", "activo")
    search_fields = ("nombre",)


@admin.register(ProveedorGasto)
class ProveedorGastoAdmin(admin.ModelAdmin):
    list_display = ("id", "negocio", "nombre", "identificacion", "activo")
    list_filter = ("negocio", "activo")
    search_fields = ("nombre", "identificacion", "email")
