from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("gastos", "0006_configcorreofactura_multi_cuenta"),
    ]

    operations = [
        migrations.AddField(
            model_name="facturagasto",
            name="alerta_ingesta",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="facturagasto",
            name="moneda",
            field=models.CharField(default="CRC", max_length=10),
        ),
        migrations.AddField(
            model_name="facturagasto",
            name="tipo_documento_xml",
            field=models.CharField(default="factura_electronica", max_length=40),
        ),
    ]
