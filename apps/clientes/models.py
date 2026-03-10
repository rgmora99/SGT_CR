from django.db import models


class TipoIdentificacion(models.Model):
    codigo = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=80)
    descripcion = models.CharField(max_length=180, blank=True)
    patron_regex = models.CharField(max_length=120, blank=True)
    ejemplo = models.CharField(max_length=60, blank=True)
    activo = models.BooleanField(default=True)
    orden = models.PositiveSmallIntegerField(default=0)

    class Meta:
        db_table = "tb_sgc_tipos_identificacion"
        ordering = ["orden", "nombre"]

    def __str__(self):
        return self.nombre


class Cliente(models.Model):
    class Estado(models.TextChoices):
        ACTIVO = "ACTIVO", "Activo"
        INACTIVO = "INACTIVO", "Inactivo"

    nombre = models.CharField(max_length=150)
    tipo_identificacion = models.ForeignKey(
        TipoIdentificacion,
        on_delete=models.PROTECT,
        related_name="clientes",
    )
    identificacion = models.CharField(max_length=30, unique=True)
    correo_electronico = models.EmailField(blank=True)
    telefono = models.CharField(max_length=25, blank=True)
    direccion = models.TextField(blank=True)
    estado = models.CharField(max_length=10, choices=Estado.choices, default=Estado.ACTIVO)
    notas = models.TextField(blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "tb_sgc_clientes"
        ordering = ["nombre"]
        constraints = [
            models.UniqueConstraint(
                fields=["tipo_identificacion", "identificacion"],
                name="uq_cliente_tipo_identificacion",
            )
        ]

    def __str__(self):
        return f"{self.nombre} ({self.identificacion})"
