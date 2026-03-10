from django.db import migrations, models
import django.db.models.deletion


def cargar_tipos_identificacion(apps, schema_editor):
    TipoIdentificacion = apps.get_model("clientes", "TipoIdentificacion")
    Cliente = apps.get_model("clientes", "Cliente")

    tipos = [
        {
            "codigo": "CED_FISICA",
            "nombre": "Cédula física",
            "descripcion": "Documento de identidad personal de Costa Rica",
            "patron_regex": r"^[1-9]-?\d{4}-?\d{4}$",
            "ejemplo": "1-1234-5678",
            "orden": 1,
        },
        {
            "codigo": "CED_JURIDICA",
            "nombre": "Cédula jurídica",
            "descripcion": "Identificación para empresas y sociedades",
            "patron_regex": r"^3-?\d{3}-?\d{6}$",
            "ejemplo": "3-101-123456",
            "orden": 2,
        },
        {
            "codigo": "DIMEX",
            "nombre": "DIMEX",
            "descripcion": "Documento de Identificación Migratorio para Extranjeros",
            "patron_regex": r"^\d{11,12}$",
            "ejemplo": "123456789012",
            "orden": 3,
        },
        {
            "codigo": "NITE",
            "nombre": "NITE",
            "descripcion": "Número de Identificación Tributaria Especial",
            "patron_regex": r"^\d{10}$",
            "ejemplo": "1234567890",
            "orden": 4,
        },
        {
            "codigo": "PASAPORTE",
            "nombre": "Pasaporte",
            "descripcion": "Documento de identificación internacional",
            "patron_regex": r"^[A-Z0-9-]{6,20}$",
            "ejemplo": "AB123456",
            "orden": 5,
        },
    ]

    for tipo in tipos:
        TipoIdentificacion.objects.update_or_create(codigo=tipo["codigo"], defaults=tipo)

    default_tipo = TipoIdentificacion.objects.get(codigo="CED_FISICA")
    Cliente.objects.filter(tipo_identificacion__isnull=True).update(tipo_identificacion=default_tipo)


class Migration(migrations.Migration):

    dependencies = [
        ("clientes", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="TipoIdentificacion",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("codigo", models.CharField(max_length=20, unique=True)),
                ("nombre", models.CharField(max_length=80)),
                ("descripcion", models.CharField(blank=True, max_length=180)),
                ("patron_regex", models.CharField(blank=True, max_length=120)),
                ("ejemplo", models.CharField(blank=True, max_length=60)),
                ("activo", models.BooleanField(default=True)),
                ("orden", models.PositiveSmallIntegerField(default=0)),
            ],
            options={
                "db_table": "tb_sgc_tipos_identificacion",
                "ordering": ["orden", "nombre"],
            },
        ),
        migrations.AddField(
            model_name="cliente",
            name="tipo_identificacion",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="clientes",
                to="clientes.tipoidentificacion",
            ),
        ),
        migrations.AlterField(
            model_name="cliente",
            name="identificacion",
            field=models.CharField(max_length=30),
        ),
        migrations.RunPython(cargar_tipos_identificacion, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="cliente",
            name="tipo_identificacion",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="clientes",
                to="clientes.tipoidentificacion",
            ),
        ),
        migrations.AddConstraint(
            model_name="cliente",
            constraint=models.UniqueConstraint(
                fields=("tipo_identificacion", "identificacion"),
                name="uq_cliente_tipo_identificacion",
            ),
        ),
    ]
