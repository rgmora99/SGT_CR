from django import forms
from .models import Alerta


class VentaForm(forms.ModelForm):

    class Meta:
        model = Alerta
        fields = [
            'tipo',
            'prioridad',
            'fecha_aviso',
            'descripcion',
            'contrato',
            'prorroga',
            'orden',
            'garantia',
            'medio',
            'dias_antelacion',
            'estado',
            'observaciones',
        ]

        widgets = {
            'fecha_aviso': forms.DateInput(attrs={'type': 'date'}),
            'descripcion': forms.Textarea(attrs={'rows': 3}),
            'observaciones': forms.Textarea(attrs={'rows': 3}),
        }
