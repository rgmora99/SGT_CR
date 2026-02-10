from django.db import models

class Auditoria(models.Model):
    usuario = models.ForeignKey("auth.User", on_delete=models.PROTECT)
    accion = models.CharField(max_length=150)
    entidad = models.CharField(max_length=100)
    fecha = models.DateTimeField(auto_now_add=True)
    detalle = models.JSONField()

    class Meta:
        db_table = "TB_SGC_AUDITORIA"

