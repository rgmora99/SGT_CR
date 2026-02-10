from django.db import models
from .contrato import Contrato


class Prorroga(models.Model):
    contrato = models.ForeignKey(
        Contrato,
        on_delete=models.CASCADE,
        related_name="prorrogas"
    )

    fecha_anterior_fin = models.DateField()
    nueva_fecha_fin = models.DateField()
    motivo = models.TextField()
    aprobada = models.BooleanField(default=False)

    class Meta:
        db_table = "tb_sgc_prorrogas"
        verbose_name = "Prórroga"
        verbose_name_plural = "Prórrogas"

    def __str__(self):
        return f"Prórroga {self.contrato.numero}"
