from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("clientes", "0002_tipoidentificacion_cliente_tipo_identificacion"),
    ]

    operations = [
        migrations.AlterField(
            model_name="cliente",
            name="identificacion",
            field=models.CharField(max_length=30, unique=True),
        ),
    ]
