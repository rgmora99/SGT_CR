from django import forms
from .models import (
    Almacen,
    CategoriaItem,
    FacturaVenta,
    Impuesto,
    LineaFacturaVenta,
    ProductoServicio,
    UnidadMedida,
)


class _NegocioScopedModelForm(forms.ModelForm):
    def __init__(self, *args, negocio_id=None, **kwargs):
        self.negocio_id = negocio_id
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            css = "form-check-input" if isinstance(field.widget, forms.CheckboxInput) else "form-control"
            field.widget.attrs["class"] = f"{field.widget.attrs.get('class', '')} {css}".strip()


class FacturaVentaForm(_NegocioScopedModelForm):
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


class ProductoServicioForm(_NegocioScopedModelForm):
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

    def __init__(self, *args, negocio_id=None, **kwargs):
        super().__init__(*args, negocio_id=negocio_id, **kwargs)
        if self.negocio_id:
            self.fields["categoria"].queryset = CategoriaItem.objects.filter(negocio_id=self.negocio_id, activo=True)
            self.fields["impuesto"].queryset = Impuesto.objects.filter(negocio_id=self.negocio_id, activo=True)

    def clean_codigo(self):
        codigo = (self.cleaned_data.get("codigo") or "").strip().upper()
        if not codigo:
            return codigo
        q = ProductoServicio.objects.filter(negocio_id=self.negocio_id, codigo__iexact=codigo)
        if self.instance.pk:
            q = q.exclude(pk=self.instance.pk)
        if q.exists():
            raise forms.ValidationError("Ya existe un producto/servicio con este código.")
        return codigo


class CategoriaItemForm(_NegocioScopedModelForm):
    class Meta:
        model = CategoriaItem
        fields = ["nombre", "descripcion", "activo"]

    def clean_nombre(self):
        nombre = (self.cleaned_data.get("nombre") or "").strip()
        q = CategoriaItem.objects.filter(negocio_id=self.negocio_id, nombre__iexact=nombre)
        if self.instance.pk:
            q = q.exclude(pk=self.instance.pk)
        if q.exists():
            raise forms.ValidationError("La categoría ya existe para este negocio.")
        return nombre


class ImpuestoForm(_NegocioScopedModelForm):
    class Meta:
        model = Impuesto
        fields = ["nombre", "porcentaje", "codigo_fiscal", "activo"]

    def clean_nombre(self):
        nombre = (self.cleaned_data.get("nombre") or "").strip()
        q = Impuesto.objects.filter(negocio_id=self.negocio_id, nombre__iexact=nombre)
        if self.instance.pk:
            q = q.exclude(pk=self.instance.pk)
        if q.exists():
            raise forms.ValidationError("El impuesto ya existe para este negocio.")
        return nombre


class AlmacenForm(_NegocioScopedModelForm):
    class Meta:
        model = Almacen
        fields = ["nombre", "ubicacion", "es_principal", "activo"]

    def clean_nombre(self):
        nombre = (self.cleaned_data.get("nombre") or "").strip()
        q = Almacen.objects.filter(negocio_id=self.negocio_id, nombre__iexact=nombre)
        if self.instance.pk:
            q = q.exclude(pk=self.instance.pk)
        if q.exists():
            raise forms.ValidationError("Ya existe un almacén con este nombre en el negocio.")
        return nombre


class UnidadMedidaForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            css = "form-check-input" if isinstance(field.widget, forms.CheckboxInput) else "form-control"
            field.widget.attrs["class"] = f"{field.widget.attrs.get('class', '')} {css}".strip()

    class Meta:
        model = UnidadMedida
        fields = ["codigo", "nombre", "permite_decimal", "activo"]

    def clean(self):
        cleaned_data = super().clean()
        codigo = (cleaned_data.get("codigo") or "").strip().upper()
        nombre = (cleaned_data.get("nombre") or "").strip()

        if codigo:
            q_codigo = UnidadMedida.objects.filter(codigo__iexact=codigo)
            if self.instance.pk:
                q_codigo = q_codigo.exclude(pk=self.instance.pk)
            if q_codigo.exists():
                self.add_error("codigo", "El código de unidad ya está registrado.")
            cleaned_data["codigo"] = codigo

        if nombre:
            q_nombre = UnidadMedida.objects.filter(nombre__iexact=nombre)
            if self.instance.pk:
                q_nombre = q_nombre.exclude(pk=self.instance.pk)
            if q_nombre.exists():
                self.add_error("nombre", "El nombre de unidad ya está registrado.")

        return cleaned_data
