from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from apps.gastos.models import FacturaGasto
from apps.gastos.forms import FiltroBandejaFacturasForm
from django.core.paginator import Paginator

@login_required
def bandeja_facturas(request):
    negocio_id = request.session.get("negocio_activo_id")

    if not negocio_id:
        return redirect("seleccionar_negocio")  # o donde manejes esto

    form = FiltroBandejaFacturasForm(request.GET or None)

    qs = FacturaGasto.objects.filter(
        negocio_id=negocio_id,
        estado__in=["pendiente", "en_registro"]
    ).order_by("-fecha_emision")

    if form.is_valid():
        q = form.cleaned_data.get("q")
        estado = form.cleaned_data.get("estado")

        if estado:
            qs = qs.filter(estado=estado)

        if q:
            qs = qs.filter(
                proveedor__icontains=q
            ) | qs.filter(numero_factura__icontains=q)

    paginator = Paginator(qs, 10)
    page_number = request.GET.get("page")
    facturas = paginator.get_page(page_number)

    return render(request, "gastos/bandeja_facturas.html", {
        "form": form,
        "facturas": facturas,
    })