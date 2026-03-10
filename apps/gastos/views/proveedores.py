from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from apps.gastos.forms.proveedores import ProveedorGastoForm
from apps.gastos.models import FacturaGasto, ProveedorGasto
from apps.gastos.services.proveedores import defaults_proveedor_desde_factura, registrar_o_recuperar_proveedor


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
        "kpi_inactivos": ProveedorGasto.objects.filter(negocio_id=negocio_id, activo=False).count(),
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
        defaults = defaults_proveedor_desde_factura(factura)
        initial["nombre"] = factura.proveedor
        initial["identificacion"] = defaults.get("identificacion") or ""
        initial["email"] = defaults.get("email") or ""
        initial["telefono"] = defaults.get("telefono") or ""

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

        return redirect("gastos:ver_proveedor", proveedor_id=proveedor.id)

    return render(
        request,
        "gastos/proveedor_form.html",
        {
            "form": form,
            "factura": factura,
            "factura_id": factura_id,
            "titulo": "Registrar proveedor",
            "accion": "Guardar proveedor",
            "es_edicion": False,
        },
    )


@login_required
def ver_proveedor(request, proveedor_id):
    negocio_id = request.session.get("negocio_activo_id")
    if not negocio_id:
        return redirect("core:home")

    proveedor = get_object_or_404(
        ProveedorGasto.objects.annotate(total_facturas=Count("facturas")),
        id=proveedor_id,
        negocio_id=negocio_id,
    )

    facturas = FacturaGasto.objects.filter(
        negocio_id=negocio_id,
        proveedor_registrado_id=proveedor_id,
    ).order_by("-fecha_emision")[:10]

    return render(
        request,
        "gastos/proveedor_detalle.html",
        {"proveedor": proveedor, "facturas": facturas},
    )


@login_required
def editar_proveedor(request, proveedor_id):
    negocio_id = request.session.get("negocio_activo_id")
    if not negocio_id:
        return redirect("core:home")

    proveedor = get_object_or_404(ProveedorGasto, id=proveedor_id, negocio_id=negocio_id)

    form = ProveedorGastoForm(request.POST or None, instance=proveedor)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Proveedor actualizado correctamente.")
        return redirect("gastos:ver_proveedor", proveedor_id=proveedor.id)

    return render(
        request,
        "gastos/proveedor_form.html",
        {
            "form": form,
            "factura": None,
            "factura_id": None,
            "titulo": "Editar proveedor",
            "accion": "Guardar cambios",
            "es_edicion": True,
            "proveedor": proveedor,
        },
    )


@login_required
def registrar_proveedor_desde_factura(request, factura_id):
    negocio_id = request.session.get("negocio_activo_id")
    if not negocio_id:
        return redirect("core:home")

    factura = get_object_or_404(FacturaGasto, id=factura_id, negocio_id=negocio_id)

    defaults = defaults_proveedor_desde_factura(factura)
    proveedor = registrar_o_recuperar_proveedor(factura.negocio, factura.proveedor, defaults=defaults)
    factura.proveedor_registrado = proveedor
    factura.save(update_fields=["proveedor_registrado"])

    messages.success(request, "Proveedor registrado automáticamente y vinculado a la factura.")
    return redirect("gastos:bandeja_facturas")


@login_required
@require_POST
def toggle_estado_proveedor(request, proveedor_id):
    negocio_id = request.session.get("negocio_activo_id")
    if not negocio_id:
        return redirect("core:home")

    proveedor = get_object_or_404(ProveedorGasto, id=proveedor_id, negocio_id=negocio_id)
    proveedor.activo = not proveedor.activo
    proveedor.save(update_fields=["activo"])

    estado = "activado" if proveedor.activo else "inactivado"
    messages.success(request, f"Proveedor {estado} correctamente.")
    return redirect(request.META.get("HTTP_REFERER") or "gastos:proveedores")
