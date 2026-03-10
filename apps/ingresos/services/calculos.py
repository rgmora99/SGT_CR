from decimal import Decimal


def calcular_totales_ingreso(detalles):
    subtotal = Decimal("0.00")
    iva = Decimal("0.00")
    total = Decimal("0.00")

    for detalle in detalles:
        subtotal += detalle.subtotal
        iva += detalle.monto_iva
        total += detalle.total_linea

    return subtotal, iva, total
