from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.accounts.models import TB_NEGOCIOS
from apps.clientes.models import Cliente
from apps.ventas.models import (
    Almacen,
    CategoriaItem,
    Existencia,
    FacturaVenta,
    Impuesto,
    LineaFacturaVenta,
    MovimientoInventario,
    ProductoServicio,
    UnidadMedida,
)
from apps.ventas.services import emitir_factura


class FacturacionInventarioTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="tester", password="123")
        self.negocio = TB_NEGOCIOS.objects.create(nombre_comercial="Demo")
        self.cliente = Cliente.objects.create(nombre="Cliente Uno", identificacion="123")
        self.categoria = CategoriaItem.objects.create(negocio=self.negocio, nombre="General")
        self.unidad = UnidadMedida.objects.create(codigo="UNI", nombre="Unidad", permite_decimal=False)
        self.impuesto = Impuesto.objects.create(negocio=self.negocio, nombre="IVA", porcentaje=Decimal("13.00"))
        self.almacen = Almacen.objects.create(negocio=self.negocio, nombre="Principal", es_principal=True)

    def test_factura_recalcula_totales(self):
        factura = FacturaVenta.objects.create(
            negocio=self.negocio,
            cliente=self.cliente,
            almacen=self.almacen,
            consecutivo="F001",
            fecha_emision="2026-01-01",
            creado_por=self.user,
        )
        producto = ProductoServicio.objects.create(
            negocio=self.negocio,
            categoria=self.categoria,
            unidad_medida=self.unidad,
            impuesto=self.impuesto,
            tipo=ProductoServicio.Tipo.PRODUCTO,
            codigo="P1",
            nombre="Producto 1",
            precio_venta=Decimal("1000.00"),
        )
        LineaFacturaVenta.objects.create(
            factura=factura,
            producto=producto,
            cantidad=Decimal("2.000"),
            precio_unitario=Decimal("1000.00"),
            porcentaje_descuento=Decimal("10.00"),
            porcentaje_impuesto=Decimal("13.00"),
            descripcion="",
        )

        factura.refresh_from_db()
        self.assertEqual(factura.subtotal, Decimal("2000.00"))
        self.assertEqual(factura.descuento_total, Decimal("200.00"))
        self.assertEqual(factura.impuesto_total, Decimal("234.00"))
        self.assertEqual(factura.total, Decimal("2034.00"))

    def test_emitir_factura_rebaja_stock(self):
        producto = ProductoServicio.objects.create(
            negocio=self.negocio,
            categoria=self.categoria,
            unidad_medida=self.unidad,
            impuesto=self.impuesto,
            tipo=ProductoServicio.Tipo.PRODUCTO,
            codigo="P2",
            nombre="Producto 2",
            precio_venta=Decimal("500.00"),
            maneja_inventario=True,
        )
        existencia = Existencia.objects.create(almacen=self.almacen, producto=producto, cantidad_disponible=Decimal("10.000"))

        factura = FacturaVenta.objects.create(
            negocio=self.negocio,
            cliente=self.cliente,
            almacen=self.almacen,
            consecutivo="F002",
            fecha_emision="2026-01-01",
            creado_por=self.user,
        )
        LineaFacturaVenta.objects.create(
            factura=factura,
            producto=producto,
            descripcion="",
            cantidad=Decimal("3.000"),
            precio_unitario=Decimal("500.00"),
            porcentaje_impuesto=Decimal("13.00"),
        )

        emitir_factura(factura, user=self.user)
        existencia.refresh_from_db()
        factura.refresh_from_db()

        self.assertEqual(factura.estado, FacturaVenta.Estado.EMITIDA)
        self.assertEqual(existencia.cantidad_disponible, Decimal("7.000"))
        self.assertTrue(MovimientoInventario.objects.filter(producto=producto, tipo=MovimientoInventario.Tipo.SALIDA).exists())

    def test_emitir_factura_con_stock_insuficiente(self):
        producto = ProductoServicio.objects.create(
            negocio=self.negocio,
            categoria=self.categoria,
            unidad_medida=self.unidad,
            impuesto=self.impuesto,
            tipo=ProductoServicio.Tipo.PRODUCTO,
            codigo="P3",
            nombre="Producto 3",
            precio_venta=Decimal("500.00"),
            maneja_inventario=True,
        )
        Existencia.objects.create(almacen=self.almacen, producto=producto, cantidad_disponible=Decimal("1.000"))
        factura = FacturaVenta.objects.create(
            negocio=self.negocio,
            cliente=self.cliente,
            almacen=self.almacen,
            consecutivo="F003",
            fecha_emision="2026-01-01",
            creado_por=self.user,
        )
        LineaFacturaVenta.objects.create(
            factura=factura,
            producto=producto,
            descripcion="",
            cantidad=Decimal("2.000"),
            precio_unitario=Decimal("500.00"),
        )

        with self.assertRaises(ValidationError):
            emitir_factura(factura, user=self.user)
