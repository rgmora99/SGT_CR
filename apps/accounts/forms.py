from django import forms
from django.contrib.auth.models import User

from apps.accounts.models import TB_NEGOCIOS

class RegisterForm(forms.Form):
    nombre = forms.CharField(max_length=150)
    apellido1 = forms.CharField(max_length=150)
    apellido2 = forms.CharField(max_length=150)
    email = forms.EmailField()
    username = forms.CharField(max_length=100)
    password1 = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("password1") != cleaned.get("password2"):
            raise forms.ValidationError("Las contraseñas no coinciden.")
        return cleaned

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Este correo ya está registrado.")
        return email

    def clean_username(self):
        username = self.cleaned_data["username"]
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Este usuario ya existe.")
        return username
    
# forms.py
from django import forms
from .models import TB_CONFIG_FISCAL_NEGOCIO

from django import forms
from .models import TB_CONFIG_FISCAL_NEGOCIO

class ConfigFiscalForm(forms.ModelForm):

    TIPO_IDENTIFICACION_CHOICES = [
        ("FISICA", "Persona física"),
        ("JURIDICA", "Persona jurídica"),
        ("DIMEX", "DIMEX"),
    ]

    REGIMEN_IVA_CHOICES = [
        ("SIMPLIFICADO", "Régimen Simplificado"),
        ("TRADICIONAL", "Régimen Tradicional"),
        ("EXENTO", "Exento"),
    ]

    PERIODO_IVA_CHOICES = [
        ("MENSUAL", "Mensual"),
        ("TRIMESTRAL", "Trimestral"),
    ]

    tipo_identificacion = forms.ChoiceField(
        choices=TIPO_IDENTIFICACION_CHOICES,
        widget=forms.Select(attrs={"class": "form-control"})
    )

    regimen_iva = forms.ChoiceField(
        choices=REGIMEN_IVA_CHOICES,
        widget=forms.Select(attrs={"class": "form-control"})
    )

    periodo_iva = forms.ChoiceField(
        choices=PERIODO_IVA_CHOICES,
        widget=forms.Select(attrs={"class": "form-control"})
    )

    aplica_iva = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"})
    )

    declara_renta = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"})
    )

    porc_iva = forms.DecimalField(
        required=False,
        max_digits=5,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            "class": "form-control",
            "placeholder": "Ej: 13",
            "step": "0.01"
        })
    )

    class Meta:
        model = TB_CONFIG_FISCAL_NEGOCIO
        fields = [
            "tipo_identificacion",
            "identificacion",
            "regimen_iva",
            "aplica_iva",
            "porc_iva",
            "periodo_iva",
            "declara_renta",
        ]
        widgets = {
            "identificacion": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Ej: 1-1111-1111"
            }),
        }

        
class NegocioForm(forms.ModelForm):
    class Meta:
        model = TB_NEGOCIOS
        fields = ["nombre_comercial", "provincia", "moneda_base"]
        widgets = {
            "nombre_comercial": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Ej. Tienda La Esquina"
            }),
            "provincia": forms.Select(attrs={
                "class": "form-control",
                "placeholder": "Opcional"
            }),
            "moneda_base": forms.Select(attrs={
                "class": "form-control"
            }),
        }