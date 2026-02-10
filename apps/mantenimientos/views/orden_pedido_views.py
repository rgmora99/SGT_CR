from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from ..models import Contrato, OrdenPedido

@login_required
def listar_ordenes(request, contrato_id):
    contrato = get_object_or_404(Contrato, id=contrato_id)
    ordenes = OrdenPedido.objects.filter(contrato=contrato)

    return render(request, "gestion_contratos/ordenes_pedido/listar_ordenes_pedido.html", {
        "contrato": contrato,
        "ordenes": ordenes
    })


@login_required
def crear_orden(request, contrato_id):
    contrato = get_object_or_404(Contrato, id=contrato_id)

    if request.method == "POST":
        OrdenPedido.objects.create(
            contrato=contrato,
            numero=request.POST["numero"],
            fecha=request.POST["fecha"],
            monto=request.POST["monto"]
        )
        return redirect("contratos:detalle", contrato_id=contrato.id)

    return render(request, "gestion_contratos/ordenes_pedido/crear_orden_pedido.html", {
        "contrato": contrato
    })
