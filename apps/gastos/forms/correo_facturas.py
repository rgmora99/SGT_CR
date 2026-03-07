from django import forms

from apps.gastos.models import ConfigCorreoFactura


class ConfigCorreoFacturaForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:
            self.fields["password"].required = True
            self.fields["password"].widget.attrs["placeholder"] = "Contraseña o App Password"

    password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Solo si deseas actualizarla",
                "autocomplete": "new-password",
            },
            render_value=False,
        ),
        help_text="Usa App Password en Gmail/Outlook para mayor seguridad.",
    )

    class Meta:
        model = ConfigCorreoFactura
        fields = [
            "nombre",
            "email",
            "password",
            "carpeta",
            "activo",
            "username",
            "imap_host",
            "imap_port",
            "imap_ssl",
        ]
        widgets = {
            "nombre": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej: Facturas compras"}),
            "email": forms.EmailInput(attrs={"class": "form-control", "placeholder": "correo@empresa.com"}),
            "carpeta": forms.TextInput(attrs={"class": "form-control", "placeholder": "INBOX"}),
            "activo": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "username": forms.TextInput(attrs={"class": "form-control"}),
            "imap_host": forms.TextInput(attrs={"class": "form-control"}),
            "imap_port": forms.NumberInput(attrs={"class": "form-control", "min": "1", "max": "65535"}),
            "imap_ssl": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def clean_imap_port(self):
        port = self.cleaned_data.get("imap_port")
        if port <= 0 or port > 65535:
            raise forms.ValidationError("Puerto IMAP inválido.")
        return port

    def clean(self):
        cleaned_data = super().clean()
        email = (cleaned_data.get("email") or "").strip().lower()

        if email and not cleaned_data.get("username"):
            cleaned_data["username"] = email

        if not cleaned_data.get("imap_host") and email:
            domain = email.split("@")[-1]
            host_by_domain = {
                "gmail.com": "imap.gmail.com",
                "outlook.com": "outlook.office365.com",
                "hotmail.com": "outlook.office365.com",
                "live.com": "outlook.office365.com",
                "yahoo.com": "imap.mail.yahoo.com",
            }
            cleaned_data["imap_host"] = host_by_domain.get(domain, f"imap.{domain}")

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        new_password = self.cleaned_data.get("password")

        if new_password:
            instance.password = new_password

        if commit:
            instance.save()

        return instance
