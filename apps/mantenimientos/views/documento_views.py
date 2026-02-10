from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages

from ..models import Contrato, ContratoDocumento


@login_required
def subir_documento(request, contrato_id):
    contrato = get_object_or_404(Contrato, id=contrato_id)

    if request.method == "POST":
        archivo = request.FILES.get("archivo")
        if not archivo:
            messages.error(request, "Debe seleccionar un archivo.")
            return redirect("contratos:lista")

        nombre = request.POST.get("nombre") or archivo.name

        ContratoDocumento.objects.create(
            contrato=contrato,
            archivo=archivo,
            nombre=nombre
        )
        messages.success(request, "Documento cargado correctamente.")
        return redirect("contratos:lista")

    messages.error(request, "Método no permitido.")
    return redirect("contratos:lista")
