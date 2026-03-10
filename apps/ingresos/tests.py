from decimal import Decimal

from django.test import TestCase

from apps.accounts.models import TB_NEGOCIOS
from apps.clientes.models import Cliente, TipoIdentificacion
from apps.ingresos.models import CategoriaIngreso, DetalleIngreso, Ingreso


class IngresosModelTests(TestCase):
    def test_calculo_detalle(self):
        negocio = TB_NEGOCIOS.objects.create(nombre_comercial="Demo")
        tipo_id = TipoIdentificacion.objects.create(codigo="GEN", nombre="Genérico")
        cliente = Cliente.objects.create(nombre="Cliente", tipo_identificacion=tipo_id, identificacion="123")
        categoria = CategoriaIngreso.objects.create(negocio=negocio, nombre="Servicios")
        ingreso = Ingreso.objects.create(
            negocio=negocio,
            cliente=cliente,
            categoria=categoria,
            consecutivo="ING-1",
            fecha_ingreso="2026-01-01",
            metodo_pago=Ingreso.MetodoPago.TRANSFERENCIA,
        )
        detalle = DetalleIngreso.objects.create(
            ingreso=ingreso,
            descripcion="Horas",
            cantidad=Decimal("2"),
            precio_unitario=Decimal("100"),
            porcentaje_iva=Decimal("13"),
        )
        self.assertEqual(detalle.subtotal, Decimal("200"))
        self.assertEqual(detalle.monto_iva, Decimal("26"))
        self.assertEqual(detalle.total_linea, Decimal("226"))
