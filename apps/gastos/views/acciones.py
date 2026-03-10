from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST

from apps.gastos.models import FacturaGasto


@login_required
@require_POST
def aprobar_factura(request, factura_id):
    factura = get_object_or_404(FacturaGasto, id=factura_id)

    if factura.estado == "rechazada":
        messages.error(request, "No puedes aprobar una factura rechazada.")
        return redirect("gastos:bandeja_facturas")

    factura.estado = "registrada"
    factura.save(update_fields=["estado"])

    messages.success(request, "Factura aprobada.")
    return redirect("gastos:bandeja_facturas")


@login_required
@require_POST
def rechazar_factura(request, factura_id):
    factura = get_object_or_404(FacturaGasto, id=factura_id)

    if factura.estado == "registrada":
        messages.error(request, "La factura ya está registrada y no se puede rechazar.")
        return redirect("gastos:bandeja_facturas")

    if factura.estado == "rechazada":
        messages.info(request, "La factura ya estaba rechazada.")
        return redirect("gastos:bandeja_facturas")

    factura.estado = "rechazada"
    factura.save(update_fields=["estado"])

    messages.warning(request, "Factura rechazada.")
    return redirect("gastos:bandeja_facturas")
