from django.contrib import admin

from .models import (
    Almacen,
    CategoriaItem,
    Existencia,
    FacturaVenta,
    Impuesto,
    LineaFacturaVenta,
    MovimientoInventario,
    ProductoServicio,
    UnidadMedida,
)


@admin.register(ProductoServicio)
class ProductoServicioAdmin(admin.ModelAdmin):
    list_display = ("codigo", "nombre", "tipo", "precio_venta", "activo")
    search_fields = ("codigo", "nombre")
    list_filter = ("tipo", "activo")


admin.site.register(CategoriaItem)
admin.site.register(UnidadMedida)
admin.site.register(Impuesto)
admin.site.register(Almacen)
admin.site.register(Existencia)
admin.site.register(FacturaVenta)
admin.site.register(LineaFacturaVenta)
admin.site.register(MovimientoInventario)
