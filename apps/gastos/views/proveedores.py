from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render

from apps.gastos.forms.proveedores import ProveedorGastoForm
from apps.gastos.models import FacturaGasto, ProveedorGasto
from apps.gastos.services.proveedores import registrar_o_recuperar_proveedor


@login_required
def listado_proveedores(request):
    negocio_id = request.session.get("negocio_activo_id")
    if not negocio_id:
        return redirect("core:home")

    q = (request.GET.get("q") or "").strip()
    proveedores = ProveedorGasto.objects.filter(negocio_id=negocio_id)

    if q:
        proveedores = proveedores.filter(
            Q(nombre__icontains=q)
            | Q(identificacion__icontains=q)
            | Q(email__icontains=q)
        )

    proveedores = proveedores.annotate(total_facturas=Count("facturas")).order_by("nombre")

    context = {
        "proveedores": proveedores,
        "q": q,
        "kpi_total": ProveedorGasto.objects.filter(negocio_id=negocio_id).count(),
        "kpi_activos": ProveedorGasto.objects.filter(negocio_id=negocio_id, activo=True).count(),
    }
    return render(request, "gastos/proveedores_listado.html", context)


@login_required
def crear_proveedor(request):
    negocio_id = request.session.get("negocio_activo_id")
    if not negocio_id:
        return redirect("core:home")

    factura_id = request.GET.get("factura") or request.POST.get("factura_id")
    factura = None
    initial = {}
    if factura_id:
        factura = get_object_or_404(FacturaGasto, id=factura_id, negocio_id=negocio_id)
        initial["nombre"] = factura.proveedor

    form = ProveedorGastoForm(request.POST or None, initial=initial)
    if request.method == "POST" and form.is_valid():
        proveedor = form.save(commit=False)
        proveedor.negocio_id = negocio_id

        proveedor_existente = ProveedorGasto.objects.filter(
            negocio_id=negocio_id,
            nombre_normalizado=proveedor.nombre.strip().lower(),
        ).first()

        if proveedor_existente:
            messages.info(request, "El proveedor ya existe, se utilizará el registro existente.")
            proveedor = proveedor_existente
        else:
            proveedor.save()
            messages.success(request, "Proveedor creado correctamente.")

        if factura:
            factura.proveedor_registrado = proveedor
            factura.save(update_fields=["proveedor_registrado"])
            messages.success(request, "Proveedor vinculado a la factura de gastos.")
            return redirect("gastos:bandeja_facturas")

        return redirect("gastos:proveedores")

    return render(
        request,
        "gastos/proveedor_form.html",
        {"form": form, "factura": factura, "factura_id": factura_id},
    )


@login_required
def registrar_proveedor_desde_factura(request, factura_id):
    negocio_id = request.session.get("negocio_activo_id")
    if not negocio_id:
        return redirect("core:home")

    factura = get_object_or_404(FacturaGasto, id=factura_id, negocio_id=negocio_id)

    proveedor = registrar_o_recuperar_proveedor(
        factura.negocio,
        factura.proveedor,
        defaults={"email": factura.email_from or None},
    )
    factura.proveedor_registrado = proveedor
    factura.save(update_fields=["proveedor_registrado"])

    messages.success(request, "Proveedor registrado automáticamente y vinculado a la factura.")
    return redirect("gastos:bandeja_facturas")
