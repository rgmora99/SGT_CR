from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0002_alter_tb_negocios_moneda_base_and_more"),
        ("gastos", "0005_gastofijo"),
    ]

    operations = [
        migrations.AddField(
            model_name="configcorreofactura",
            name="nombre",
            field=models.CharField(default="Correo principal", max_length=100),
        ),
        migrations.AlterField(
            model_name="configcorreofactura",
            name="negocio",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="correo_facturas",
                to="accounts.tb_negocios",
            ),
        ),
        migrations.AddConstraint(
            model_name="configcorreofactura",
            constraint=models.UniqueConstraint(
                fields=("negocio", "email"),
                name="uniq_config_correo_por_negocio_email",
            ),
        ),
    ]
