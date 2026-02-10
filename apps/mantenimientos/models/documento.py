from django.db import models
from .contrato import Contrato



class ContratoDocumento(models.Model):
    contrato = models.ForeignKey(
        Contrato,
        on_delete=models.CASCADE,
        related_name="documentos",
    )

    archivo = models.FileField(upload_to="contratos/documentos/")
    nombre = models.CharField(max_length=255, blank=True)
    subido_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "tb_sgc_contratos_documentos"
        verbose_name = "Documento de contrato"
        verbose_name_plural = "Documentos de contrato"
        ordering = ["-subido_en"]

    def __str__(self):
        return self.nombre or self.archivo.name
