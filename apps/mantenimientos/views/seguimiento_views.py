from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404

from ..models import (
    Contrato,
    Garantia,
    OrdenPedido,
    Prorroga,
    ContratoDocumento
)


@login_required
def seguimiento_contrato(request, contrato_id):
    contrato = get_object_or_404(Contrato, id=contrato_id)

    contexto = {
        "contrato": contrato,
        "documentos": contrato.documentos.all(),
        "garantias": contrato.garantias.all(),
        "ordenes": contrato.ordenes_pedido.all(),
        "prorrogas": contrato.prorrogas.all(),
    }

    return render(
        request,
        "contratos/seguimiento_contrato.html",
        contexto
    )
