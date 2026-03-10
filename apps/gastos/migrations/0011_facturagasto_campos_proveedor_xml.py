from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("gastos", "0010_proveedorgasto_facturagasto_proveedor_registrado"),
    ]

    operations = [
        migrations.AddField(
            model_name="facturagasto",
            name="proveedor_email",
            field=models.EmailField(blank=True, max_length=254, null=True),
        ),
        migrations.AddField(
            model_name="facturagasto",
            name="proveedor_identificacion",
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name="facturagasto",
            name="proveedor_telefono",
            field=models.CharField(blank=True, max_length=25, null=True),
        ),
    ]
