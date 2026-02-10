from django.db import models

class Proveedor(models.Model):
    razon_social = models.CharField(max_length=255)
    identificacion = models.CharField(max_length=50, unique=True)

    class Meta:
        db_table = "tb_sgc_proveedores"
        ordering = ["razon_social"]

    def __str__(self):
        return self.razon_social
