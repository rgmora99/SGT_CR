from decimal import Decimal

from django.db.models import Q, Sum
from django.db.models.functions import Coalesce

from apps.gastos.models import Gasto
from apps.ventas.models import FacturaVenta


def _filtro_periodo(anio, mes=None):
    filtro = Q(fecha__year=anio)
    if mes:
        filtro &= Q(fecha__month=mes)
    return filtro


def calcular_resumen_fiscal(negocio_id, anio, mes=None, tasa_renta=Decimal("0.30")):
    filtro_gasto = Q(fecha_gasto__year=anio)
    filtro_venta = Q(fecha_emision__year=anio)
    if mes:
        filtro_gasto &= Q(fecha_gasto__month=mes)
        filtro_venta &= Q(fecha_emision__month=mes)

    gastos = Gasto.objects.filter(negocio_id=negocio_id, estado="registrado").filter(filtro_gasto)
    ventas = (
        FacturaVenta.objects.filter(negocio_id=negocio_id)
        .exclude(estado=FacturaVenta.Estado.ANULADA)
        .filter(filtro_venta)
    )

    compras_gravadas = gastos.filter(iva__gt=0).aggregate(total=Coalesce(Sum("subtotal"), Decimal("0.00")))["total"]
    compras_exentas = gastos.filter(iva=0).aggregate(total=Coalesce(Sum("subtotal"), Decimal("0.00")))["total"]
    credito_fiscal = gastos.aggregate(total=Coalesce(Sum("iva"), Decimal("0.00")))["total"]

    ventas_gravadas = ventas.filter(impuesto_total__gt=0).aggregate(total=Coalesce(Sum("subtotal"), Decimal("0.00")))["total"]
    ventas_exentas = ventas.filter(impuesto_total=0).aggregate(total=Coalesce(Sum("subtotal"), Decimal("0.00")))["total"]
    debito_fiscal = ventas.aggregate(total=Coalesce(Sum("impuesto_total"), Decimal("0.00")))["total"]

    iva_por_pagar = debito_fiscal - credito_fiscal

    total_gastos = gastos.aggregate(total=Coalesce(Sum("total"), Decimal("0.00")))["total"]
    total_ventas = ventas.aggregate(total=Coalesce(Sum("total"), Decimal("0.00")))["total"]

    utilidad_proyectada = total_ventas - total_gastos
    impuesto_renta_proyectado = Decimal("0.00")
    if utilidad_proyectada > 0 and tasa_renta > 0:
        impuesto_renta_proyectado = (utilidad_proyectada * tasa_renta).quantize(Decimal("0.01"))

    return {
        "compras_gravadas": compras_gravadas,
        "compras_exentas": compras_exentas,
        "credito_fiscal": credito_fiscal,
        "ventas_gravadas": ventas_gravadas,
        "ventas_exentas": ventas_exentas,
        "debito_fiscal": debito_fiscal,
        "iva_por_pagar": iva_por_pagar,
        "utilidad_proyectada": utilidad_proyectada,
        "impuesto_renta_proyectado": impuesto_renta_proyectado,
    }
