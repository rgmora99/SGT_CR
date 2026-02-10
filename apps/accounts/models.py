from django.conf import settings
from django.db import models

class TB_USUARIOS_APP(models.Model):
    id_usuario_app = models.BigAutoField(primary_key=True, db_column="ID_USUARIO_APP")
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        db_column="ID_AUTH_USER",
        related_name="perfil_app",
    )
    telefono = models.CharField(max_length=30, null=True, blank=True, db_column="TELEFONO")
    fecha_registro = models.DateTimeField(auto_now_add=True, db_column="FECHA_REGISTRO")

    class Meta:
        db_table = 'cnt"."TB_USUARIOS_APP'  # importante para schema
        managed = True

class TB_NEGOCIOS(models.Model):
    MONEDAS = [
        ("CRC", "Colones (CRC)"),
        ("USD", "Dólares (USD)"),
    ]

    PROVINCIAS = [
        ("SJO", "San José (SJO)"),
        ("ALJ", "Alajuela (ALJ)"),
        ("HER", "Heredia (HER)"),
        ("GUA", "Guanacaste (GUA)"),
        ("CAR", "Cartago (CAR)"),
        ("PUN", "Puntarenas (PUN)"),
        ("LIM", "Limón (LIM)"),
    ]

    id_negocio = models.BigAutoField(primary_key=True, db_column="ID_NEGOCIO")
    nombre_comercial = models.CharField(max_length=150, db_column="NOMBRE_COMERCIAL")
    provincia = models.CharField(
        max_length=20,
        default="SJO",
        choices=PROVINCIAS,
        db_column="PROVINCIA"
    )

    moneda_base = models.CharField(
        max_length=10,
        default="CRC",
        choices=MONEDAS,
        db_column="MONEDA_BASE"
    )

    created_at = models.DateTimeField(auto_now_add=True, db_column="CREATED_AT")

    class Meta:
        db_table = 'cnt"."TB_NEGOCIOS'
        managed = True

class TB_USUARIO_NEGOCIO(models.Model):
    id_usuario_negocio = models.BigAutoField(primary_key=True, db_column="ID_USUARIO_NEGOCIO")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        db_column="ID_AUTH_USER",
        related_name="negocios",
    )
    negocio = models.ForeignKey(
        TB_NEGOCIOS,
        on_delete=models.CASCADE,
        db_column="ID_NEGOCIO",
        related_name="usuarios",
    )
    rol_en_negocio = models.CharField(max_length=50, default="OWNER", db_column="ROL_EN_NEGOCIO")

    class Meta:
        db_table = 'cnt"."TB_USUARIO_NEGOCIO'
        managed = True
        constraints = [
            models.UniqueConstraint(fields=["user", "negocio"], name="UK_USER_NEG")
        ]

class TB_CONFIG_FISCAL_NEGOCIO(models.Model):
    id_config_fiscal = models.BigAutoField(primary_key=True, db_column="ID_CONFIG_FISCAL")
    negocio = models.OneToOneField(
        TB_NEGOCIOS,
        on_delete=models.CASCADE,
        db_column="ID_NEGOCIO",
        related_name="config_fiscal",
    )

    tipo_identificacion = models.CharField(max_length=20, null=True, blank=True, db_column="TIPO_IDENTIFICACION")
    identificacion = models.CharField(max_length=30, null=True, blank=True, db_column="IDENTIFICACION")
    regimen_iva = models.CharField(max_length=50, null=True, blank=True, db_column="REGIMEN_IVA")
    aplica_iva = models.BooleanField(default=True, db_column="APLICA_IVA")
    porc_iva = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, db_column="PORC_IVA")

    periodo_iva = models.CharField(max_length=20, default="MENSUAL", db_column="PERIODO_IVA")
    declara_renta = models.BooleanField(default=True, db_column="DECLARA_RENTA")

    created_at = models.DateTimeField(auto_now_add=True, db_column="CREATED_AT")

    class Meta:
        db_table = 'cnt"."TB_CONFIG_FISCAL_NEGOCIO'
        managed = True
