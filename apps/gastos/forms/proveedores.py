from django import forms

from apps.gastos.models import ProveedorGasto


class ProveedorGastoForm(forms.ModelForm):
    class Meta:
        model = ProveedorGasto
        fields = ["nombre", "identificacion", "email", "telefono", "activo"]
        widgets = {
            "nombre": forms.TextInput(attrs={"class": "form-control", "placeholder": "Nombre del proveedor"}),
            "identificacion": forms.TextInput(attrs={"class": "form-control", "placeholder": "Cédula o identificación"}),
            "email": forms.EmailInput(attrs={"class": "form-control", "placeholder": "correo@proveedor.com"}),
            "telefono": forms.TextInput(attrs={"class": "form-control", "placeholder": "8888-8888"}),
            "activo": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def clean_nombre(self):
        return (self.cleaned_data.get("nombre") or "").strip()
