from django.db import models
from .contrato import Contrato


class OrdenPedido(models.Model):
    contrato = models.ForeignKey(
        Contrato,
        on_delete=models.CASCADE,
        related_name="ordenes_pedido"
    )

    numero_orden = models.CharField(max_length=50, unique=True)
    fecha_orden = models.DateField()
    monto = models.DecimalField(max_digits=18, decimal_places=2)
    descripcion = models.TextField(blank=True)

    class Meta:
        db_table = "tb_sgc_ordenes_pedido"
        verbose_name = "Orden de Pedido"
        verbose_name_plural = "Órdenes de Pedido"

    def __str__(self):
        return self.numero_orden
