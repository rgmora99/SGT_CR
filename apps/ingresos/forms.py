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
            "cliente": forms.Select(attrs={"class": "form-select"}),
            "categoria": forms.Select(attrs={"class": "form-select"}),
            "consecutivo": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej: ING-2026-0001"}),
            "fecha_ingreso": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "fecha_vencimiento": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "moneda": forms.TextInput(attrs={"class": "form-control"}),
            "tipo_cambio": forms.NumberInput(attrs={"class": "form-control", "step": "0.0001", "min": "0"}),
            "metodo_pago": forms.Select(attrs={"class": "form-select"}),
            "referencia_externa": forms.TextInput(attrs={"class": "form-control"}),
            "notas": forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
            "estado": forms.Select(attrs={"class": "form-select"}),
        }

    def __init__(self, *args, negocio_id=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["categoria"].queryset = CategoriaIngreso.objects.filter(negocio_id=negocio_id, activo=True)


class DetalleIngresoForm(forms.ModelForm):
    class Meta:
        model = DetalleIngreso
        fields = ["descripcion", "cantidad", "precio_unitario", "porcentaje_iva"]
        widgets = {
            "descripcion": forms.TextInput(attrs={"class": "form-control", "placeholder": "Detalle del servicio o producto"}),
            "cantidad": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "min": "0.01", "placeholder": "Cantidad"}),
            "precio_unitario": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "min": "0", "placeholder": "Precio unitario"}),
            "porcentaje_iva": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "min": "0"}),
        }

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
