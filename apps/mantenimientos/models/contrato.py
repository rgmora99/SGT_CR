from django.db import models

class Contrato(models.Model):
    class TipoContrato(models.TextChoices):
        BIENES = "BIENES", "Bienes"
        SERVICIOS = "SERVICIOS", "Servicios"
        CONSULTORIA = "CONSULTORIA", "Consultoría"

    class EstadoContrato(models.TextChoices):
        ACTIVO = "ACTIVO", "Activo"
        PRORROGA = "PRORROGA", "En prórroga"
        VENCIDO = "VENCIDO", "Vencido"

    numero = models.CharField("Número de contrato", max_length=50, unique=True)
    contratista = models.CharField("Contratista", max_length=255)
    gerencia = models.CharField("Gerencia", max_length=120)
    objeto = models.TextField("Objeto del contrato")

    fecha_inicio = models.DateField("Fecha inicio")
    fecha_fin = models.DateField("Fecha fin")

    monto = models.DecimalField("Monto (₡)", max_digits=18, decimal_places=2)

    tipo = models.CharField(
        "Tipo de contrato", max_length=20,
        choices=TipoContrato.choices, default=TipoContrato.BIENES
    )

    estado = models.CharField(
        "Estado", max_length=20,
        choices=EstadoContrato.choices, default=EstadoContrato.ACTIVO
    )

    notas = models.TextField("Condiciones / Observaciones", blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "tb_sgc_contratos"
        verbose_name = "Contrato"
        verbose_name_plural = "Contratos"
        ordering = ["-created_at"]

    def __str__(self):
        return self.numero

