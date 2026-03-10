from django import forms

from .models import Cliente


class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = [
            "nombre",
            "identificacion",
            "correo_electronico",
            "telefono",
            "direccion",
            "estado",
            "notas",
        ]
        widgets = {
            "nombre": forms.TextInput(attrs={"class": "form-control", "placeholder": "Nombre completo o razón social"}),
            "identificacion": forms.TextInput(attrs={"class": "form-control", "placeholder": "Cédula física o jurídica"}),
            "correo_electronico": forms.EmailInput(attrs={"class": "form-control", "placeholder": "correo@empresa.com"}),
            "telefono": forms.TextInput(attrs={"class": "form-control", "placeholder": "8888-8888"}),
            "direccion": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Dirección de contacto"}),
            "estado": forms.Select(attrs={"class": "form-select"}),
            "notas": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Información adicional (opcional)"}),
        }
