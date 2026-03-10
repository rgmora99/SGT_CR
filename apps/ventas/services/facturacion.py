from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction

from apps.ventas.models import Existencia, FacturaVenta, MovimientoInventario


def registrar_movimiento_inventario(*, existencia, tipo, cantidad, referencia, user=None, observaciones=""):
    if cantidad <= Decimal("0.000"):
        raise ValidationError("La cantidad debe ser mayor que cero.")

    if tipo == MovimientoInventario.Tipo.ENTRADA:
        existencia.cantidad_disponible += cantidad
    elif tipo == MovimientoInventario.Tipo.SALIDA:
        if existencia.cantidad_libre < cantidad:
            raise ValidationError(f"Stock insuficiente para {existencia.producto.nombre}.")
        existencia.cantidad_disponible -= cantidad
    elif tipo == MovimientoInventario.Tipo.AJUSTE:
        existencia.cantidad_disponible = cantidad
    else:
        raise ValidationError("Tipo de movimiento no soportado.")

    existencia.save(update_fields=["cantidad_disponible", "actualizado_en"])

    MovimientoInventario.objects.create(
        negocio=existencia.almacen.negocio,
        almacen=existencia.almacen,
        producto=existencia.producto,
        tipo=tipo,
        cantidad=cantidad,
        referencia=referencia,
        observaciones=observaciones,
        creado_por=user,
    )


def emitir_factura(factura: FacturaVenta, user=None):
    if factura.estado != FacturaVenta.Estado.BORRADOR:
        raise ValidationError("Solo se pueden emitir facturas en estado borrador.")

    if not factura.lineas.exists():
        raise ValidationError("La factura no tiene líneas para emitir.")

    with transaction.atomic():
        for linea in factura.lineas.select_related("producto"):
            producto = linea.producto
            if not producto or not producto.maneja_inventario:
                continue

            if not factura.almacen_id:
                raise ValidationError("La factura requiere almacén para rebajar inventario.")

            existencia, _ = Existencia.objects.select_for_update().get_or_create(
                almacen=factura.almacen,
                producto=producto,
                defaults={"cantidad_disponible": Decimal("0.000")},
            )

            registrar_movimiento_inventario(
                existencia=existencia,
                tipo=MovimientoInventario.Tipo.SALIDA,
                cantidad=linea.cantidad,
                referencia=f"Factura {factura.consecutivo}",
                user=user,
            )

        factura.estado = FacturaVenta.Estado.EMITIDA
        factura.save(update_fields=["estado", "actualizado_en"])

    return factura
