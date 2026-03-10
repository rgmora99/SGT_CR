from datetime import timedelta
from decimal import Decimal

from django.test import TestCase
from django.utils import timezone

from apps.accounts.models import TB_NEGOCIOS
from apps.clientes.models import Cliente
from apps.ingresos.forms import IngresoForm
from apps.ingresos.models import CategoriaIngreso, DetalleIngreso, Ingreso
from apps.ingresos.views import _extraer_tipo_cambio


class IngresosModelTests(TestCase):
    def test_calculo_detalle(self):
        negocio = TB_NEGOCIOS.objects.create(nombre_comercial="Demo")
        cliente = Cliente.objects.create(nombre="Cliente", identificacion="123")
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


class IngresoFormTests(TestCase):
    def setUp(self):
        self.negocio = TB_NEGOCIOS.objects.create(nombre_comercial="Negocio")
        self.cliente = Cliente.objects.create(nombre="Cliente", identificacion="321")
        self.categoria = CategoriaIngreso.objects.create(negocio=self.negocio, nombre="Servicios")

    def _base_data(self, fecha):
        return {
            "cliente": self.cliente.id,
            "categoria": self.categoria.id,
            "consecutivo": "ING-2026-0001",
            "fecha_ingreso": fecha,
            "fecha_vencimiento": "",
            "moneda": Ingreso.Moneda.CRC,
            "tipo_cambio": "",
            "metodo_pago": Ingreso.MetodoPago.EFECTIVO,
            "referencia_externa": "",
            "notas": "",
            "estado": Ingreso.Estado.BORRADOR,
        }

    def test_fecha_ingreso_debe_ser_hoy(self):
        ayer = (timezone.localdate() - timedelta(days=1)).isoformat()
        form = IngresoForm(data=self._base_data(ayer), negocio_id=self.negocio.id)
        self.assertFalse(form.is_valid())
        self.assertIn("fecha_ingreso", form.errors)

    def test_fecha_ingreso_hoy_es_valida(self):
        hoy = timezone.localdate().isoformat()
        form = IngresoForm(data=self._base_data(hoy), negocio_id=self.negocio.id)
        self.assertTrue(form.is_valid())


class TipoCambioParserTests(TestCase):
    def test_extrae_hacienda(self):
        valor, fuente = _extraer_tipo_cambio({"venta": {"valor": "536.12"}})
        self.assertEqual(valor, 536.12)
        self.assertEqual(fuente, "hacienda")

    def test_extrae_rates(self):
        valor, fuente = _extraer_tipo_cambio({"rates": {"CRC": 537.55}})
        self.assertEqual(valor, 537.55)
        self.assertEqual(fuente, "fx")
