from decimal import Decimal

from django import forms
from django.core.exceptions import ValidationError
from django.forms import BaseInlineFormSet, inlineformset_factory
from django.utils import timezone

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
            self.fields["fecha_ingreso"].initial = timezone.localdate()
        self.fields["consecutivo"].help_text = "Se genera automáticamente al guardar."

    def clean(self):
        cleaned_data = super().clean()
        moneda = cleaned_data.get("moneda")
        tipo_cambio = cleaned_data.get("tipo_cambio")
        fecha_ingreso = cleaned_data.get("fecha_ingreso")

        if fecha_ingreso and fecha_ingreso != timezone.localdate():
            self.add_error("fecha_ingreso", "La fecha de ingreso debe ser la fecha actual.")

        if moneda == Ingreso.Moneda.USD:
            if not tipo_cambio or tipo_cambio <= 0:
                self.add_error("tipo_cambio", "Para ingresos en USD debes indicar un tipo de cambio mayor a cero.")
        else:
            cleaned_data["tipo_cambio"] = None

        return cleaned_data


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
        if self.cleaned_data.get("DELETE"):
            return cleaned_data

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

    def clean(self):
        super().clean()
        if any(self.errors):
            return

        filas_validas = 0
        for form in self.forms:
            if form.cleaned_data.get("DELETE"):
                continue

            producto = form.cleaned_data.get("producto")
            descripcion = (form.cleaned_data.get("descripcion") or "").strip()
            cantidad = form.cleaned_data.get("cantidad")
            precio_unitario = form.cleaned_data.get("precio_unitario")

            if producto or descripcion or cantidad or precio_unitario:
                filas_validas += 1

        if filas_validas == 0:
            raise ValidationError("Debes agregar al menos una línea de detalle antes de guardar.")


DetalleIngresoFormSet = inlineformset_factory(
    Ingreso,
    DetalleIngreso,
    form=DetalleIngresoForm,
    formset=DetalleIngresoBaseFormSet,
    extra=1,
    can_delete=True,
)
