from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

from apps.accounts.models import TB_NEGOCIOS
from apps.clientes.models import Cliente


class CategoriaIngreso(models.Model):
    negocio = models.ForeignKey(TB_NEGOCIOS, on_delete=models.CASCADE, related_name="categorias_ingreso")
    nombre = models.CharField(max_length=120)
    descripcion = models.TextField(blank=True)
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ["nombre"]
        constraints = [
            models.UniqueConstraint(fields=["negocio", "nombre"], name="uq_categoria_ingreso_negocio_nombre"),
        ]

    def __str__(self):
        return self.nombre


class ProductoIngreso(models.Model):
    negocio = models.ForeignKey(TB_NEGOCIOS, on_delete=models.CASCADE, related_name="productos_ingreso")
    codigo = models.CharField(max_length=40)
    nombre = models.CharField(max_length=150)
    precio_base = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ["nombre"]
        constraints = [
            models.UniqueConstraint(fields=["negocio", "codigo"], name="uq_producto_ingreso_negocio_codigo"),
        ]

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


class Ingreso(models.Model):
    class MetodoPago(models.TextChoices):
        EFECTIVO = "EFECTIVO", "Efectivo"
        TRANSFERENCIA = "TRANSFERENCIA", "Transferencia"
        TARJETA = "TARJETA", "Tarjeta"
        SINPE = "SINPE", "SINPE"
        CUOTAS = "CUOTAS", "A cuotas"

    class Estado(models.TextChoices):
        BORRADOR = "BORRADOR", "Borrador"
        CONFIRMADO = "CONFIRMADO", "Confirmado"
        ANULADO = "ANULADO", "Anulado"

    class Moneda(models.TextChoices):
        CRC = "CRC", "Colones (CRC)"
        USD = "USD", "Dólares (USD)"

    negocio = models.ForeignKey(TB_NEGOCIOS, on_delete=models.CASCADE, related_name="ingresos")
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, related_name="ingresos")
    categoria = models.ForeignKey(CategoriaIngreso, on_delete=models.PROTECT, related_name="ingresos")

    consecutivo = models.CharField(max_length=50)
    fecha_ingreso = models.DateField()
    fecha_vencimiento = models.DateField(null=True, blank=True)

    moneda = models.CharField(max_length=10, default=Moneda.CRC, choices=Moneda.choices)
    tipo_cambio = models.DecimalField(max_digits=12, decimal_places=4, null=True, blank=True)

    subtotal = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    iva = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    total = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))

    metodo_pago = models.CharField(max_length=20, choices=MetodoPago.choices)
    estado = models.CharField(max_length=20, choices=Estado.choices, default=Estado.BORRADOR)

    referencia_externa = models.CharField(max_length=80, blank=True)
    notas = models.TextField(blank=True)

    creado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="ingresos_creados")
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-fecha_ingreso", "-id"]
        constraints = [
            models.UniqueConstraint(fields=["negocio", "consecutivo"], name="uq_ingreso_negocio_consecutivo"),
        ]
        indexes = [
            models.Index(fields=["negocio", "fecha_ingreso"]),
            models.Index(fields=["negocio", "estado"]),
        ]

    def __str__(self):
        return f"Ingreso {self.consecutivo}"

    @classmethod
    def generar_consecutivo(cls, negocio_id, year):
        prefijo = f"ING-{year}-"
        ultimo = (
            cls.objects.filter(negocio_id=negocio_id, consecutivo__startswith=prefijo)
            .order_by("-consecutivo")
            .values_list("consecutivo", flat=True)
            .first()
        )
        ultimo_num = int(ultimo.split("-")[-1]) if ultimo and ultimo.split("-")[-1].isdigit() else 0
        return f"{prefijo}{ultimo_num + 1:04d}"


class DetalleIngreso(models.Model):
    ingreso = models.ForeignKey(Ingreso, on_delete=models.CASCADE, related_name="detalles")
    producto = models.ForeignKey(ProductoIngreso, on_delete=models.PROTECT, related_name="detalles", null=True, blank=True)
    descripcion = models.CharField(max_length=200)
    cantidad = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))])
    precio_unitario = models.DecimalField(max_digits=14, decimal_places=2, validators=[MinValueValidator(Decimal("0.00"))])
    porcentaje_iva = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("13.00"), validators=[MinValueValidator(Decimal("0.00"))])

    subtotal = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    monto_iva = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    total_linea = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))

    class Meta:
        ordering = ["id"]

    def calcular_totales(self):
        self.subtotal = (self.cantidad or Decimal("0.00")) * (self.precio_unitario or Decimal("0.00"))
        self.monto_iva = self.subtotal * ((self.porcentaje_iva or Decimal("0.00")) / Decimal("100"))
        self.total_linea = self.subtotal + self.monto_iva

    def save(self, *args, **kwargs):
        if self.producto and not self.descripcion:
            self.descripcion = self.producto.nombre
        self.calcular_totales()
        super().save(*args, **kwargs)
