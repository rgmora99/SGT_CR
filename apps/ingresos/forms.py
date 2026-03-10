from decimal import Decimal

from django import forms
from django.forms import BaseInlineFormSet, inlineformset_factory

from .models import CategoriaIngreso, DetalleIngreso, Ingreso, ProductoIngreso


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
            "consecutivo": forms.TextInput(attrs={"class": "form-control", "readonly": "readonly"}),
            "fecha_ingreso": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "fecha_vencimiento": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "moneda": forms.Select(attrs={"class": "form-select"}),
            "tipo_cambio": forms.NumberInput(attrs={"class": "form-control", "step": "0.0001", "min": "0"}),
            "metodo_pago": forms.Select(attrs={"class": "form-select"}),
            "referencia_externa": forms.TextInput(attrs={"class": "form-control"}),
            "notas": forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
            "estado": forms.Select(attrs={"class": "form-select"}),
        }

    def __init__(self, *args, negocio_id=None, consecutivo_sugerido=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["categoria"].queryset = CategoriaIngreso.objects.filter(negocio_id=negocio_id, activo=True)
        if not self.instance.pk:
            self.fields["consecutivo"].initial = consecutivo_sugerido
        self.fields["consecutivo"].help_text = "Se genera automáticamente al guardar."


class DetalleIngresoForm(forms.ModelForm):
    class Meta:
        model = DetalleIngreso
        fields = ["producto", "descripcion", "cantidad", "precio_unitario", "porcentaje_iva"]
        widgets = {
            "producto": forms.Select(attrs={"class": "form-select js-producto"}),
            "descripcion": forms.TextInput(attrs={"class": "form-control", "placeholder": "Detalle del servicio o producto"}),
            "cantidad": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "min": "0.01", "placeholder": "Cantidad"}),
            "precio_unitario": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "min": "0", "placeholder": "Precio unitario"}),
            "porcentaje_iva": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "min": "0"}),
        }

    def __init__(self, *args, negocio_id=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["producto"].queryset = ProductoIngreso.objects.filter(negocio_id=negocio_id, activo=True)
        self.fields["producto"].required = False

    def clean(self):
        cleaned_data = super().clean()
        cantidad = cleaned_data.get("cantidad") or Decimal("0")
        if cantidad <= 0:
            self.add_error("cantidad", "La cantidad debe ser mayor a cero.")

        producto = cleaned_data.get("producto")
        if producto and not cleaned_data.get("descripcion"):
            cleaned_data["descripcion"] = producto.nombre
        return cleaned_data


class DetalleIngresoBaseFormSet(BaseInlineFormSet):
    def __init__(self, *args, negocio_id=None, **kwargs):
        self.negocio_id = negocio_id
        super().__init__(*args, **kwargs)

    def _construct_form(self, i, **kwargs):
        kwargs["negocio_id"] = self.negocio_id
        return super()._construct_form(i, **kwargs)


DetalleIngresoFormSet = inlineformset_factory(
    Ingreso,
    DetalleIngreso,
    form=DetalleIngresoForm,
    formset=DetalleIngresoBaseFormSet,
    extra=1,
    can_delete=True,
)
