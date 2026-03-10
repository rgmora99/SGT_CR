from django.contrib import admin

from .models import CategoriaIngreso, DetalleIngreso, Ingreso


class DetalleIngresoInline(admin.TabularInline):
    model = DetalleIngreso
    extra = 0


@admin.register(Ingreso)
class IngresoAdmin(admin.ModelAdmin):
    list_display = ("consecutivo", "negocio", "cliente", "fecha_ingreso", "total", "estado")
    list_filter = ("estado", "metodo_pago", "moneda")
    search_fields = ("consecutivo", "cliente__nombre")
    inlines = [DetalleIngresoInline]


@admin.register(CategoriaIngreso)
class CategoriaIngresoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "negocio", "activo")
    list_filter = ("activo",)
