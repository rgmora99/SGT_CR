from django.db import models
from .contrato import Contrato


class Garantia(models.Model):
    class TipoGarantia(models.TextChoices):
        CUMPLIMIENTO = "CUMPLIMIENTO", "Cumplimiento"
        PARTICIPACION = "PARTICIPACION", "Participación"
        CALIDAD = "CALIDAD", "Calidad"

    contrato = models.ForeignKey(
        Contrato,
        on_delete=models.CASCADE,
        related_name="garantias"
    )

    tipo = models.CharField(
        max_length=30,
        choices=TipoGarantia.choices
    )

    monto = models.DecimalField(max_digits=18, decimal_places=2)
    entidad_emisora = models.CharField(max_length=255)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    observaciones = models.TextField(blank=True)

    class Meta:
        db_table = "tb_sgc_garantias"
        verbose_name = "Garantía"
        verbose_name_plural = "Garantías"

    def __str__(self):
        return f"{self.tipo} - {self.contrato.numero}"
