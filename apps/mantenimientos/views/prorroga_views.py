from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from ..models import Contrato, Prorroga

@login_required
def listar_prorrogas(request, contrato_id):
    contrato = get_object_or_404(Contrato, id=contrato_id)
    prorrogas = Prorroga.objects.filter(contrato=contrato)

    return render(request, "gestion_contratos/prorrogas/listar_prorrogas.html", {
        "contrato": contrato,
        "prorrogas": prorrogas
    })


@login_required
def crear_prorroga(request, contrato_id):
    contrato = get_object_or_404(Contrato, id=contrato_id)

    if request.method == "POST":
        Prorroga.objects.create(
            contrato=contrato,
            fecha_inicio=request.POST["fecha_inicio"],
            fecha_fin=request.POST["fecha_fin"],
            motivo=request.POST["motivo"]
        )

        # Cambiar estado automáticamente
        contrato.estado = "PRORROGA"
        contrato.save()

        return redirect("contratos:detalle", contrato_id=contrato.id)

    return render(request, "gestion_contratos/prorrogas/crear_prorroga.html", {
        "contrato": contrato
    })
