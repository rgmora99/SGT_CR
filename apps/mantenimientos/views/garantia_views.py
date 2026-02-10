from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from ..models import Contrato, Garantia

@login_required
def listar_garantias(request, contrato_id):
    contrato = get_object_or_404(Contrato, id=contrato_id)
    garantias = Garantia.objects.filter(contrato=contrato)

    return render(request, "gestion_contratos/garantias/listar_garantias.html", {
        "contrato": contrato,
        "garantias": garantias
    })


@login_required
def crear_garantia(request, contrato_id):
    contrato = get_object_or_404(Contrato, id=contrato_id)

    if request.method == "POST":
        Garantia.objects.create(
            contrato=contrato,
            tipo=request.POST["tipo"],
            monto=request.POST["monto"],
            fecha_vencimiento=request.POST["fecha_vencimiento"]
        )
        return redirect("contratos:detalle", contrato_id=contrato.id)

    return render(request, "gestion_contratos/garantias/crear_garantia.html", {
        "contrato": contrato
    })
