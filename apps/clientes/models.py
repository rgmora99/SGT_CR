from django.db import models


class Cliente(models.Model):
    class Estado(models.TextChoices):
        ACTIVO = "ACTIVO", "Activo"
        INACTIVO = "INACTIVO", "Inactivo"

    nombre = models.CharField(max_length=150)
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

    def __str__(self):
        return f"{self.nombre} ({self.identificacion})"
