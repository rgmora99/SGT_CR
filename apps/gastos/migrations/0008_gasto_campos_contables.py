from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("gastos", "0007_facturagasto_moneda_alertas_tipo_xml"),
    ]

    operations = [
        migrations.AddField(
            model_name="gasto",
            name="referencia_contable",
            field=models.CharField(blank=True, max_length=80, null=True),
        ),
        migrations.AddField(
            model_name="gasto",
            name="tipo_cambio",
            field=models.DecimalField(blank=True, decimal_places=4, max_digits=12, null=True),
        ),
        migrations.AddField(
            model_name="gasto",
            name="total_moneda_base",
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True),
        ),
    ]
