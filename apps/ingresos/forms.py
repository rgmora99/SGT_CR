from decimal import Decimal

from django import forms
from django.forms import inlineformset_factory

from .models import CategoriaIngreso, DetalleIngreso, Ingreso


class IngresoForm(forms.ModelForm):
    class Meta:
        model = Ingreso
        fields = [
            "cliente",
            "categoria",
            "consecutivo",
            "fecha_ingreso",
            "fecha_vencimiento",
            "moneda",
            "tipo_cambio",
            "metodo_pago",
            "referencia_externa",
            "notas",
            "estado",
        ]
        widgets = {
            "fecha_ingreso": forms.DateInput(attrs={"type": "date"}),
            "fecha_vencimiento": forms.DateInput(attrs={"type": "date"}),
            "notas": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, negocio_id=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["categoria"].queryset = CategoriaIngreso.objects.filter(negocio_id=negocio_id, activo=True)


class DetalleIngresoForm(forms.ModelForm):
    class Meta:
        model = DetalleIngreso
        fields = ["descripcion", "cantidad", "precio_unitario", "porcentaje_iva"]

    def clean(self):
        cleaned_data = super().clean()
        cantidad = cleaned_data.get("cantidad") or Decimal("0")
        if cantidad <= 0:
            self.add_error("cantidad", "La cantidad debe ser mayor a cero.")
        return cleaned_data


DetalleIngresoFormSet = inlineformset_factory(
    Ingreso,
    DetalleIngreso,
    form=DetalleIngresoForm,
    extra=1,
    can_delete=True,
)
