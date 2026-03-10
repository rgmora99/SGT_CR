import re

from django import forms
from django.core.exceptions import ValidationError

from .models import Cliente


class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = [
            "nombre",
            "tipo_identificacion",
            "identificacion",
            "correo_electronico",
            "telefono",
            "direccion",
            "estado",
            "notas",
        ]
        widgets = {
            "nombre": forms.TextInput(attrs={"class": "form-control", "placeholder": "Nombre completo o razón social"}),
            "tipo_identificacion": forms.Select(attrs={"class": "form-select"}),
            "identificacion": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ingrese la identificación sin espacios"}),
            "correo_electronico": forms.EmailInput(attrs={"class": "form-control", "placeholder": "correo@empresa.com"}),
            "telefono": forms.TextInput(attrs={"class": "form-control", "placeholder": "8888-8888 o +506 8888-8888"}),
            "direccion": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Dirección de contacto"}),
            "estado": forms.Select(attrs={"class": "form-select"}),
            "notas": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Información adicional (opcional)"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["tipo_identificacion"].empty_label = "Seleccione un tipo"
        self.fields["tipo_identificacion"].queryset = self.fields["tipo_identificacion"].queryset.filter(activo=True)

    def clean_nombre(self):
        nombre = " ".join(self.cleaned_data["nombre"].split())
        if len(nombre) < 3:
            raise ValidationError("Ingrese un nombre o razón social válido (mínimo 3 caracteres).")
        return nombre

    def clean_identificacion(self):
        identificacion = re.sub(r"\s+", "", self.cleaned_data["identificacion"].upper())
        if not re.fullmatch(r"[A-Z0-9-]{5,30}", identificacion):
            raise ValidationError("La identificación solo puede contener letras, números y guiones.")
        return identificacion

    def clean_telefono(self):
        telefono = self.cleaned_data.get("telefono", "").strip()
        if telefono and not re.fullmatch(r"\+?[0-9\-\s()]{8,20}", telefono):
            raise ValidationError("Ingrese un teléfono válido (solo dígitos, espacios y guiones).")
        return telefono

    def clean(self):
        cleaned_data = super().clean()
        tipo_identificacion = cleaned_data.get("tipo_identificacion")
        identificacion = cleaned_data.get("identificacion", "")

        if tipo_identificacion and identificacion and tipo_identificacion.patron_regex:
            if not re.fullmatch(tipo_identificacion.patron_regex, identificacion):
                ejemplo = f" Ejemplo: {tipo_identificacion.ejemplo}." if tipo_identificacion.ejemplo else ""
                self.add_error(
                    "identificacion",
                    f"La identificación no cumple el formato esperado para {tipo_identificacion.nombre}.{ejemplo}",
                )

        return cleaned_data
