from django import forms

from .models import FacturaVenta, LineaFacturaVenta, ProductoServicio


class FacturaVentaForm(forms.ModelForm):
    class Meta:
        model = FacturaVenta
        fields = [
            "cliente",
            "almacen",
            "consecutivo",
            "fecha_emision",
            "fecha_vencimiento",
            "moneda",
            "tipo_cambio",
            "notas",
        ]
        widgets = {
            "fecha_emision": forms.DateInput(attrs={"type": "date"}),
            "fecha_vencimiento": forms.DateInput(attrs={"type": "date"}),
            "notas": forms.Textarea(attrs={"rows": 3}),
        }


class LineaFacturaVentaForm(forms.ModelForm):
    class Meta:
        model = LineaFacturaVenta
        fields = [
            "producto",
            "descripcion",
            "cantidad",
            "precio_unitario",
            "porcentaje_descuento",
            "porcentaje_impuesto",
        ]


class ProductoServicioForm(forms.ModelForm):
    class Meta:
        model = ProductoServicio
        fields = [
            "categoria",
            "unidad_medida",
            "impuesto",
            "tipo",
            "codigo",
            "nombre",
            "descripcion",
            "precio_venta",
            "costo_referencia",
            "maneja_inventario",
            "stock_minimo",
            "stock_maximo",
            "activo",
        ]
