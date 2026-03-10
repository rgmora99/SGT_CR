from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Sum
from django.db.models.functions import Coalesce

from apps.accounts.models import TB_NEGOCIOS
from apps.clientes.models import Cliente


class CategoriaItem(models.Model):
    negocio = models.ForeignKey(TB_NEGOCIOS, on_delete=models.CASCADE, related_name="categorias_items")
    nombre = models.CharField(max_length=120)
    descripcion = models.TextField(blank=True)
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ["nombre"]
        constraints = [
            models.UniqueConstraint(fields=["negocio", "nombre"], name="uq_categoria_item_negocio_nombre"),
        ]

    def __str__(self):
        return self.nombre


class UnidadMedida(models.Model):
    codigo = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=80)
    permite_decimal = models.BooleanField(default=True)
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Impuesto(models.Model):
    negocio = models.ForeignKey(TB_NEGOCIOS, on_delete=models.CASCADE, related_name="impuestos_venta")
    nombre = models.CharField(max_length=80)
    porcentaje = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(Decimal("0.00"))])
    codigo_fiscal = models.CharField(max_length=20, blank=True)
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ["nombre"]
        constraints = [
            models.UniqueConstraint(fields=["negocio", "nombre"], name="uq_impuesto_negocio_nombre"),
        ]

    def __str__(self):
        return f"{self.nombre} ({self.porcentaje}%)"


class ProductoServicio(models.Model):
    class Tipo(models.TextChoices):
        PRODUCTO = "PRODUCTO", "Producto"
        SERVICIO = "SERVICIO", "Servicio"

    negocio = models.ForeignKey(TB_NEGOCIOS, on_delete=models.CASCADE, related_name="productos_servicios")
    categoria = models.ForeignKey(CategoriaItem, on_delete=models.PROTECT, related_name="productos")
    unidad_medida = models.ForeignKey(UnidadMedida, on_delete=models.PROTECT, related_name="productos")
    impuesto = models.ForeignKey(Impuesto, on_delete=models.PROTECT, related_name="productos", null=True, blank=True)

    tipo = models.CharField(max_length=10, choices=Tipo.choices)
    codigo = models.CharField(max_length=40)
    nombre = models.CharField(max_length=160)
    descripcion = models.TextField(blank=True)

    precio_venta = models.DecimalField(max_digits=14, decimal_places=2, validators=[MinValueValidator(Decimal("0.00"))])
    costo_referencia = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
    )

    maneja_inventario = models.BooleanField(default=True)
    stock_minimo = models.DecimalField(max_digits=12, decimal_places=3, default=Decimal("0.000"))
    stock_maximo = models.DecimalField(max_digits=12, decimal_places=3, null=True, blank=True)
    activo = models.BooleanField(default=True)

    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["nombre"]
        constraints = [
            models.UniqueConstraint(fields=["negocio", "codigo"], name="uq_producto_negocio_codigo"),
        ]

    def save(self, *args, **kwargs):
        if self.tipo == self.Tipo.SERVICIO:
            self.maneja_inventario = False
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


class Almacen(models.Model):
    negocio = models.ForeignKey(TB_NEGOCIOS, on_delete=models.CASCADE, related_name="almacenes")
    nombre = models.CharField(max_length=120)
    ubicacion = models.CharField(max_length=180, blank=True)
    es_principal = models.BooleanField(default=False)
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ["nombre"]
        constraints = [
            models.UniqueConstraint(fields=["negocio", "nombre"], name="uq_almacen_negocio_nombre"),
        ]

    def __str__(self):
        return self.nombre


class Existencia(models.Model):
    almacen = models.ForeignKey(Almacen, on_delete=models.CASCADE, related_name="existencias")
    producto = models.ForeignKey(ProductoServicio, on_delete=models.CASCADE, related_name="existencias")
    cantidad_disponible = models.DecimalField(max_digits=12, decimal_places=3, default=Decimal("0.000"))
    cantidad_reservada = models.DecimalField(max_digits=12, decimal_places=3, default=Decimal("0.000"))
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["almacen", "producto"], name="uq_existencia_almacen_producto"),
        ]
        indexes = [
            models.Index(fields=["almacen", "producto"]),
        ]

    @property
    def cantidad_libre(self):
        return (self.cantidad_disponible or Decimal("0.000")) - (self.cantidad_reservada or Decimal("0.000"))


class FacturaVenta(models.Model):
    class Estado(models.TextChoices):
        BORRADOR = "BORRADOR", "Borrador"
        EMITIDA = "EMITIDA", "Emitida"
        PAGADA = "PAGADA", "Pagada"
        ANULADA = "ANULADA", "Anulada"

    negocio = models.ForeignKey(TB_NEGOCIOS, on_delete=models.CASCADE, related_name="facturas_venta")
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, related_name="facturas_venta")
    almacen = models.ForeignKey(Almacen, on_delete=models.PROTECT, related_name="facturas_venta", null=True, blank=True)

    consecutivo = models.CharField(max_length=50)
    fecha_emision = models.DateField()
    fecha_vencimiento = models.DateField(null=True, blank=True)

    moneda = models.CharField(max_length=10, default="CRC")
    tipo_cambio = models.DecimalField(max_digits=12, decimal_places=4, null=True, blank=True)

    estado = models.CharField(max_length=20, choices=Estado.choices, default=Estado.BORRADOR)

    subtotal = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    descuento_total = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    impuesto_total = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    total = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))

    notas = models.TextField(blank=True)
    creado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="facturas_creadas")
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-fecha_emision", "-id"]
        constraints = [
            models.UniqueConstraint(fields=["negocio", "consecutivo"], name="uq_factura_venta_negocio_consecutivo"),
        ]
        indexes = [
            models.Index(fields=["negocio", "fecha_emision"]),
            models.Index(fields=["negocio", "estado"]),
        ]

    def recalcular_totales(self):
        agregados = self.lineas.aggregate(
            subtotal=Coalesce(Sum("subtotal"), Decimal("0.00")),
            descuento=Coalesce(Sum("monto_descuento"), Decimal("0.00")),
            impuesto=Coalesce(Sum("monto_impuesto"), Decimal("0.00")),
            total=Coalesce(Sum("total_linea"), Decimal("0.00")),
        )
        self.subtotal = agregados["subtotal"]
        self.descuento_total = agregados["descuento"]
        self.impuesto_total = agregados["impuesto"]
        self.total = agregados["total"]
        self.save(update_fields=["subtotal", "descuento_total", "impuesto_total", "total", "actualizado_en"])

    def __str__(self):
        return f"Factura {self.consecutivo}"


class LineaFacturaVenta(models.Model):
    factura = models.ForeignKey(FacturaVenta, on_delete=models.CASCADE, related_name="lineas")
    producto = models.ForeignKey(ProductoServicio, on_delete=models.PROTECT, related_name="lineas_factura", null=True, blank=True)

    descripcion = models.CharField(max_length=200)
    cantidad = models.DecimalField(max_digits=12, decimal_places=3, validators=[MinValueValidator(Decimal("0.001"))])
    precio_unitario = models.DecimalField(max_digits=14, decimal_places=2, validators=[MinValueValidator(Decimal("0.00"))])

    porcentaje_descuento = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.00"))
    porcentaje_impuesto = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.00"))

    subtotal = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    monto_descuento = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    monto_impuesto = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    total_linea = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))

    class Meta:
        ordering = ["id"]

    def calcular_totales(self):
        self.subtotal = (self.cantidad or Decimal("0.000")) * (self.precio_unitario or Decimal("0.00"))
        self.monto_descuento = self.subtotal * ((self.porcentaje_descuento or Decimal("0.00")) / Decimal("100"))
        base_impuesto = self.subtotal - self.monto_descuento
        self.monto_impuesto = base_impuesto * ((self.porcentaje_impuesto or Decimal("0.00")) / Decimal("100"))
        self.total_linea = base_impuesto + self.monto_impuesto

    def save(self, *args, **kwargs):
        if self.producto and not self.descripcion:
            self.descripcion = self.producto.nombre
        if self.producto and self.porcentaje_impuesto == Decimal("0.00") and self.producto.impuesto:
            self.porcentaje_impuesto = self.producto.impuesto.porcentaje
        self.calcular_totales()
        super().save(*args, **kwargs)
        self.factura.recalcular_totales()


class MovimientoInventario(models.Model):
    class Tipo(models.TextChoices):
        ENTRADA = "ENTRADA", "Entrada"
        SALIDA = "SALIDA", "Salida"
        AJUSTE = "AJUSTE", "Ajuste"

    negocio = models.ForeignKey(TB_NEGOCIOS, on_delete=models.CASCADE, related_name="movimientos_inventario")
    almacen = models.ForeignKey(Almacen, on_delete=models.PROTECT, related_name="movimientos")
    producto = models.ForeignKey(ProductoServicio, on_delete=models.PROTECT, related_name="movimientos")
    tipo = models.CharField(max_length=20, choices=Tipo.choices)
    cantidad = models.DecimalField(max_digits=12, decimal_places=3, validators=[MinValueValidator(Decimal("0.001"))])

    referencia = models.CharField(max_length=80, blank=True)
    observaciones = models.TextField(blank=True)
    creado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="movimientos_inventario_creados")
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-creado_en", "-id"]
        indexes = [
            models.Index(fields=["negocio", "producto", "creado_en"]),
        ]
