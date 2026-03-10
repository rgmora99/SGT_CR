from decimal import Decimal

from django.db import models

from apps.accounts.models import TB_NEGOCIOS


class CierreFiscalPeriodo(models.Model):
    class Tipo(models.TextChoices):
        MENSUAL = "MENSUAL", "Mensual"
        ANUAL = "ANUAL", "Anual"

    class Estado(models.TextChoices):
        BORRADOR = "BORRADOR", "Borrador"
        CERRADO = "CERRADO", "Cerrado"

    negocio = models.ForeignKey(TB_NEGOCIOS, on_delete=models.CASCADE, related_name="cierres_fiscales")
    tipo = models.CharField(max_length=10, choices=Tipo.choices, default=Tipo.MENSUAL)
    anio = models.PositiveIntegerField()
    mes = models.PositiveSmallIntegerField(null=True, blank=True)

    estado = models.CharField(max_length=10, choices=Estado.choices, default=Estado.BORRADOR)

    compras_gravadas = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    compras_exentas = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    credito_fiscal = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))

    ventas_gravadas = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    ventas_exentas = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    debito_fiscal = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))

    iva_por_pagar = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    utilidad_proyectada = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    impuesto_renta_proyectado = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))

    observaciones = models.TextField(blank=True)
    cerrado_en = models.DateTimeField(null=True, blank=True)

    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-anio", "-mes", "tipo"]
        constraints = [
            models.UniqueConstraint(
                fields=["negocio", "tipo", "anio", "mes"],
                name="uq_cierre_fiscal_negocio_tipo_anio_mes",
            )
        ]

    def __str__(self):
        periodo = f"{self.anio}-{str(self.mes).zfill(2)}" if self.tipo == self.Tipo.MENSUAL else str(self.anio)
        return f"{self.negocio} / {self.tipo} / {periodo}"
