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
            name="CategoriaIngreso",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("nombre", models.CharField(max_length=120)),
                ("descripcion", models.TextField(blank=True)),
                ("activo", models.BooleanField(default=True)),
                (
                    "negocio",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="categorias_ingreso", to="accounts.tb_negocios"),
                ),
            ],
            options={"ordering": ["nombre"]},
        ),
        migrations.CreateModel(
            name="Ingreso",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("consecutivo", models.CharField(max_length=50)),
                ("fecha_ingreso", models.DateField()),
                ("fecha_vencimiento", models.DateField(blank=True, null=True)),
                ("moneda", models.CharField(default="CRC", max_length=10)),
                ("tipo_cambio", models.DecimalField(blank=True, decimal_places=4, max_digits=12, null=True)),
                ("subtotal", models.DecimalField(decimal_places=2, default=Decimal("0.00"), max_digits=14)),
                ("iva", models.DecimalField(decimal_places=2, default=Decimal("0.00"), max_digits=14)),
                ("total", models.DecimalField(decimal_places=2, default=Decimal("0.00"), max_digits=14)),
                (
                    "metodo_pago",
                    models.CharField(
                        choices=[
                            ("EFECTIVO", "Efectivo"),
                            ("TRANSFERENCIA", "Transferencia"),
                            ("TARJETA", "Tarjeta"),
                            ("SINPE", "SINPE"),
                        ],
                        max_length=20,
                    ),
                ),
                (
                    "estado",
                    models.CharField(
                        choices=[("BORRADOR", "Borrador"), ("CONFIRMADO", "Confirmado"), ("ANULADO", "Anulado")],
                        default="BORRADOR",
                        max_length=20,
                    ),
                ),
                ("referencia_externa", models.CharField(blank=True, max_length=80)),
                ("notas", models.TextField(blank=True)),
                ("creado_en", models.DateTimeField(auto_now_add=True)),
                ("actualizado_en", models.DateTimeField(auto_now=True)),
                (
                    "categoria",
                    models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="ingresos", to="ingresos.categoriaingreso"),
                ),
                (
                    "cliente",
                    models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="ingresos", to="clientes.cliente"),
                ),
                (
                    "creado_por",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="ingresos_creados",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "negocio",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="ingresos", to="accounts.tb_negocios"),
                ),
            ],
            options={"ordering": ["-fecha_ingreso", "-id"]},
        ),
        migrations.CreateModel(
            name="DetalleIngreso",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("descripcion", models.CharField(max_length=200)),
                (
                    "cantidad",
                    models.DecimalField(
                        decimal_places=2,
                        max_digits=12,
                        validators=[django.core.validators.MinValueValidator(Decimal("0.01"))],
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
                (
                    "porcentaje_iva",
                    models.DecimalField(
                        decimal_places=2,
                        default=Decimal("13.00"),
                        max_digits=5,
                        validators=[django.core.validators.MinValueValidator(Decimal("0.00"))],
                    ),
                ),
                ("subtotal", models.DecimalField(decimal_places=2, default=Decimal("0.00"), max_digits=14)),
                ("monto_iva", models.DecimalField(decimal_places=2, default=Decimal("0.00"), max_digits=14)),
                ("total_linea", models.DecimalField(decimal_places=2, default=Decimal("0.00"), max_digits=14)),
                (
                    "ingreso",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="detalles", to="ingresos.ingreso"),
                ),
            ],
            options={"ordering": ["id"]},
        ),
        migrations.AddConstraint(
            model_name="categoriaingreso",
            constraint=models.UniqueConstraint(fields=("negocio", "nombre"), name="uq_categoria_ingreso_negocio_nombre"),
        ),
        migrations.AddConstraint(
            model_name="ingreso",
            constraint=models.UniqueConstraint(fields=("negocio", "consecutivo"), name="uq_ingreso_negocio_consecutivo"),
        ),
        migrations.AddIndex(
            model_name="ingreso",
            index=models.Index(fields=["negocio", "fecha_ingreso"], name="ingresos_ing_negocio_3d2dcf_idx"),
        ),
        migrations.AddIndex(
            model_name="ingreso",
            index=models.Index(fields=["negocio", "estado"], name="ingresos_ing_negocio_381ef6_idx"),
        ),
    ]
