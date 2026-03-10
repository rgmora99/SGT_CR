from decimal import Decimal

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("accounts", "0002_alter_tb_negocios_moneda_base_and_more"),
        ("clientes", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="UnidadMedida",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("codigo", models.CharField(max_length=20, unique=True)),
                ("nombre", models.CharField(max_length=80)),
                ("permite_decimal", models.BooleanField(default=True)),
                ("activo", models.BooleanField(default=True)),
            ],
            options={"ordering": ["nombre"]},
        ),
        migrations.CreateModel(
            name="CategoriaItem",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("nombre", models.CharField(max_length=120)),
                ("descripcion", models.TextField(blank=True)),
                ("activo", models.BooleanField(default=True)),
                (
                    "negocio",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="categorias_items", to="accounts.tb_negocios"),
                ),
            ],
            options={"ordering": ["nombre"]},
        ),
        migrations.CreateModel(
            name="Almacen",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("nombre", models.CharField(max_length=120)),
                ("ubicacion", models.CharField(blank=True, max_length=180)),
                ("es_principal", models.BooleanField(default=False)),
                ("activo", models.BooleanField(default=True)),
                (
                    "negocio",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="almacenes", to="accounts.tb_negocios"),
                ),
            ],
            options={"ordering": ["nombre"]},
        ),
        migrations.CreateModel(
            name="Impuesto",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("nombre", models.CharField(max_length=80)),
                (
                    "porcentaje",
                    models.DecimalField(
                        decimal_places=2,
                        max_digits=5,
                        validators=[django.core.validators.MinValueValidator(Decimal("0.00"))],
                    ),
                ),
                ("codigo_fiscal", models.CharField(blank=True, max_length=20)),
                ("activo", models.BooleanField(default=True)),
                (
                    "negocio",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="impuestos_venta", to="accounts.tb_negocios"),
                ),
            ],
            options={"ordering": ["nombre"]},
        ),
        migrations.CreateModel(
            name="ProductoServicio",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("tipo", models.CharField(choices=[("PRODUCTO", "Producto"), ("SERVICIO", "Servicio")], max_length=10)),
                ("codigo", models.CharField(max_length=40)),
                ("nombre", models.CharField(max_length=160)),
                ("descripcion", models.TextField(blank=True)),
                (
                    "precio_venta",
                    models.DecimalField(
                        decimal_places=2,
                        max_digits=14,
                        validators=[django.core.validators.MinValueValidator(Decimal("0.00"))],
                    ),
                ),
                (
                    "costo_referencia",
                    models.DecimalField(
                        decimal_places=2,
                        default=Decimal("0.00"),
                        max_digits=14,
                        validators=[django.core.validators.MinValueValidator(Decimal("0.00"))],
                    ),
                ),
                ("maneja_inventario", models.BooleanField(default=True)),
                ("stock_minimo", models.DecimalField(decimal_places=3, default=Decimal("0.000"), max_digits=12)),
                ("stock_maximo", models.DecimalField(blank=True, decimal_places=3, max_digits=12, null=True)),
                ("activo", models.BooleanField(default=True)),
                ("creado_en", models.DateTimeField(auto_now_add=True)),
                ("actualizado_en", models.DateTimeField(auto_now=True)),
                (
                    "categoria",
                    models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="productos", to="ventas.categoriaitem"),
                ),
                (
                    "impuesto",
                    models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="productos", to="ventas.impuesto"),
                ),
                (
                    "negocio",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="productos_servicios", to="accounts.tb_negocios"),
                ),
                (
                    "unidad_medida",
                    models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="productos", to="ventas.unidadmedida"),
                ),
            ],
            options={"ordering": ["nombre"]},
        ),
        migrations.CreateModel(
            name="FacturaVenta",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("consecutivo", models.CharField(max_length=50)),
                ("fecha_emision", models.DateField()),
                ("fecha_vencimiento", models.DateField(blank=True, null=True)),
                ("moneda", models.CharField(default="CRC", max_length=10)),
                ("tipo_cambio", models.DecimalField(blank=True, decimal_places=4, max_digits=12, null=True)),
                (
                    "estado",
                    models.CharField(
                        choices=[("BORRADOR", "Borrador"), ("EMITIDA", "Emitida"), ("PAGADA", "Pagada"), ("ANULADA", "Anulada")],
                        default="BORRADOR",
                        max_length=20,
                    ),
                ),
                ("subtotal", models.DecimalField(decimal_places=2, default=Decimal("0.00"), max_digits=14)),
                ("descuento_total", models.DecimalField(decimal_places=2, default=Decimal("0.00"), max_digits=14)),
                ("impuesto_total", models.DecimalField(decimal_places=2, default=Decimal("0.00"), max_digits=14)),
                ("total", models.DecimalField(decimal_places=2, default=Decimal("0.00"), max_digits=14)),
                ("notas", models.TextField(blank=True)),
                ("creado_en", models.DateTimeField(auto_now_add=True)),
                ("actualizado_en", models.DateTimeField(auto_now=True)),
                (
                    "almacen",
                    models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="facturas_venta", to="ventas.almacen"),
                ),
                (
                    "cliente",
                    models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="facturas_venta", to="clientes.cliente"),
                ),
                (
                    "creado_por",
                    models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="facturas_creadas", to=settings.AUTH_USER_MODEL),
                ),
                (
                    "negocio",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="facturas_venta", to="accounts.tb_negocios"),
                ),
            ],
            options={"ordering": ["-fecha_emision", "-id"]},
        ),
        migrations.CreateModel(
            name="LineaFacturaVenta",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("descripcion", models.CharField(max_length=200)),
                (
                    "cantidad",
                    models.DecimalField(
                        decimal_places=3,
                        max_digits=12,
                        validators=[django.core.validators.MinValueValidator(Decimal("0.001"))],
                    ),
                ),
                (
                    "precio_unitario",
                    models.DecimalField(
                        decimal_places=2,
                        max_digits=14,
                        validators=[django.core.validators.MinValueValidator(Decimal("0.00"))],
                    ),
                ),
                ("porcentaje_descuento", models.DecimalField(decimal_places=2, default=Decimal("0.00"), max_digits=5)),
                ("porcentaje_impuesto", models.DecimalField(decimal_places=2, default=Decimal("0.00"), max_digits=5)),
                ("subtotal", models.DecimalField(decimal_places=2, default=Decimal("0.00"), max_digits=14)),
                ("monto_descuento", models.DecimalField(decimal_places=2, default=Decimal("0.00"), max_digits=14)),
                ("monto_impuesto", models.DecimalField(decimal_places=2, default=Decimal("0.00"), max_digits=14)),
                ("total_linea", models.DecimalField(decimal_places=2, default=Decimal("0.00"), max_digits=14)),
                (
                    "factura",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="lineas", to="ventas.facturaventa"),
                ),
                (
                    "producto",
                    models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="lineas_factura", to="ventas.productoservicio"),
                ),
            ],
            options={"ordering": ["id"]},
        ),
        migrations.CreateModel(
            name="Existencia",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("cantidad_disponible", models.DecimalField(decimal_places=3, default=Decimal("0.000"), max_digits=12)),
                ("cantidad_reservada", models.DecimalField(decimal_places=3, default=Decimal("0.000"), max_digits=12)),
                ("actualizado_en", models.DateTimeField(auto_now=True)),
                (
                    "almacen",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="existencias", to="ventas.almacen"),
                ),
                (
                    "producto",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="existencias", to="ventas.productoservicio"),
                ),
            ],
        ),
        migrations.CreateModel(
            name="MovimientoInventario",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("tipo", models.CharField(choices=[("ENTRADA", "Entrada"), ("SALIDA", "Salida"), ("AJUSTE", "Ajuste")], max_length=20)),
                (
                    "cantidad",
                    models.DecimalField(
                        decimal_places=3,
                        max_digits=12,
                        validators=[django.core.validators.MinValueValidator(Decimal("0.001"))],
                    ),
                ),
                ("referencia", models.CharField(blank=True, max_length=80)),
                ("observaciones", models.TextField(blank=True)),
                ("creado_en", models.DateTimeField(auto_now_add=True)),
                (
                    "almacen",
                    models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="movimientos", to="ventas.almacen"),
                ),
                (
                    "creado_por",
                    models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="movimientos_inventario_creados", to=settings.AUTH_USER_MODEL),
                ),
                (
                    "negocio",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="movimientos_inventario", to="accounts.tb_negocios"),
                ),
                (
                    "producto",
                    models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="movimientos", to="ventas.productoservicio"),
                ),
            ],
            options={"ordering": ["-creado_en", "-id"]},
        ),
        migrations.AddConstraint(
            model_name="categoriaitem",
            constraint=models.UniqueConstraint(fields=("negocio", "nombre"), name="uq_categoria_item_negocio_nombre"),
        ),
        migrations.AddConstraint(
            model_name="almacen",
            constraint=models.UniqueConstraint(fields=("negocio", "nombre"), name="uq_almacen_negocio_nombre"),
        ),
        migrations.AddConstraint(
            model_name="impuesto",
            constraint=models.UniqueConstraint(fields=("negocio", "nombre"), name="uq_impuesto_negocio_nombre"),
        ),
        migrations.AddConstraint(
            model_name="productoservicio",
            constraint=models.UniqueConstraint(fields=("negocio", "codigo"), name="uq_producto_negocio_codigo"),
        ),
        migrations.AddConstraint(
            model_name="facturaventa",
            constraint=models.UniqueConstraint(fields=("negocio", "consecutivo"), name="uq_factura_venta_negocio_consecutivo"),
        ),
        migrations.AddConstraint(
            model_name="existencia",
            constraint=models.UniqueConstraint(fields=("almacen", "producto"), name="uq_existencia_almacen_producto"),
        ),
        migrations.AddIndex(
            model_name="facturaventa",
            index=models.Index(fields=["negocio", "fecha_emision"], name="ventas_fact_negocio_97f58c_idx"),
        ),
        migrations.AddIndex(
            model_name="facturaventa",
            index=models.Index(fields=["negocio", "estado"], name="ventas_fact_negocio_16d8a7_idx"),
        ),
        migrations.AddIndex(
            model_name="existencia",
            index=models.Index(fields=["almacen", "producto"], name="ventas_exis_almacen_8a1e7c_idx"),
        ),
        migrations.AddIndex(
            model_name="movimientoinventario",
            index=models.Index(fields=["negocio", "producto", "creado_en"], name="ventas_movi_negocio_59e900_idx"),
        ),
    ]
