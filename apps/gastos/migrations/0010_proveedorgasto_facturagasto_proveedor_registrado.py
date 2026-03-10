from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("gastos", "0009_merge_20260309_1841"),
    ]

    operations = [
        migrations.CreateModel(
            name="ProveedorGasto",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("nombre", models.CharField(max_length=180)),
                ("nombre_normalizado", models.CharField(max_length=180)),
                ("identificacion", models.CharField(blank=True, max_length=50, null=True)),
                ("email", models.EmailField(blank=True, max_length=254, null=True)),
                ("telefono", models.CharField(blank=True, max_length=25, null=True)),
                ("activo", models.BooleanField(default=True)),
                ("creado_en", models.DateTimeField(auto_now_add=True)),
                (
                    "negocio",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="proveedores_gasto",
                        to="accounts.tb_negocios",
                    ),
                ),
            ],
            options={
                "ordering": ["nombre"],
            },
        ),
        migrations.AddField(
            model_name="facturagasto",
            name="proveedor_registrado",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="facturas",
                to="gastos.proveedorgasto",
            ),
        ),
        migrations.AddConstraint(
            model_name="proveedorgasto",
            constraint=models.UniqueConstraint(
                fields=("negocio", "nombre_normalizado"),
                name="uniq_proveedor_gasto_nombre_por_negocio",
            ),
        ),
        migrations.AddIndex(
            model_name="proveedorgasto",
            index=models.Index(fields=["negocio", "activo"], name="gastos_prove_negocio_0f5de1_idx"),
        ),
        migrations.AddIndex(
            model_name="proveedorgasto",
            index=models.Index(fields=["negocio", "nombre_normalizado"], name="gastos_prove_negocio_50860c_idx"),
        ),
    ]
