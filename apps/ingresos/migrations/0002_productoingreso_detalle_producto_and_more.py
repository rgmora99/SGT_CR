from decimal import Decimal

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0002_alter_tb_negocios_moneda_base_and_more"),
        ("ingresos", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="ProductoIngreso",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("codigo", models.CharField(max_length=40)),
                ("nombre", models.CharField(max_length=150)),
                ("precio_base", models.DecimalField(decimal_places=2, default=Decimal("0.00"), max_digits=14)),
                ("activo", models.BooleanField(default=True)),
                (
                    "negocio",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="productos_ingreso", to="accounts.tb_negocios"),
                ),
            ],
            options={"ordering": ["nombre"]},
        ),
        migrations.AddField(
            model_name="detalleingreso",
            name="producto",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="detalles", to="ingresos.productoingreso"),
        ),
        migrations.AlterField(
            model_name="ingreso",
            name="metodo_pago",
            field=models.CharField(
                choices=[
                    ("EFECTIVO", "Efectivo"),
                    ("TRANSFERENCIA", "Transferencia"),
                    ("TARJETA", "Tarjeta"),
                    ("SINPE", "SINPE"),
                    ("CUOTAS", "A cuotas"),
                ],
                max_length=20,
            ),
        ),
        migrations.AlterField(
            model_name="ingreso",
            name="moneda",
            field=models.CharField(
                choices=[("CRC", "Colones (CRC)"), ("USD", "Dólares (USD)")], default="CRC", max_length=10
            ),
        ),
        migrations.AddConstraint(
            model_name="productoingreso",
            constraint=models.UniqueConstraint(fields=("negocio", "codigo"), name="uq_producto_ingreso_negocio_codigo"),
        ),
    ]
