from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from django.utils.dateparse import parse_date
from django.shortcuts import get_object_or_404, redirect, render

from apps.gastos.models import CategoriaGasto, FacturaGasto, Gasto
from apps.gastos.services.proveedores import registrar_o_recuperar_proveedor


MONEDA_SIMBOLOS = {
    "CRC": "₡",
    "USD": "$",
    "EUR": "€",
}


def _simbolo_moneda(codigo):
    return MONEDA_SIMBOLOS.get((codigo or "").upper(), (codigo or ""))


@login_required
@transaction.atomic
def registrar_gasto(request, factura_id):
    factura = (
        FacturaGasto.objects.select_for_update().select_related("negocio").get(id=factura_id)
    )

    if hasattr(factura, "gasto"):
        return redirect("gastos:ver_gasto", factura.gasto.id)

    if factura.estado == "pendiente":
        factura.estado = "en_registro"
        factura.save(update_fields=["estado"])

    categorias = CategoriaGasto.objects.filter(negocio=factura.negocio, activo=True)

    draft = {
        "categoria": "",
        "fecha_gasto": factura.fecha_emision.isoformat() if factura.fecha_emision else "",
        "metodo_pago": "",
        "referencia_contable": factura.numero_factura or "",
        "tipo_cambio": "1.0000" if (factura.moneda or "CRC") == factura.negocio.moneda_base else "",
        "notas": "",
    }

    if request.method == "POST":
        has_error = False
        draft.update(
            {
                "categoria": (request.POST.get("categoria") or "").strip(),
                "fecha_gasto": (request.POST.get("fecha_gasto") or "").strip(),
                "metodo_pago": (request.POST.get("metodo_pago") or "").strip(),
                "referencia_contable": (request.POST.get("referencia_contable") or "").strip(),
                "tipo_cambio": (request.POST.get("tipo_cambio") or "").strip(),
                "notas": (request.POST.get("notas") or "").strip(),
            }
        )

        categoria = CategoriaGasto.objects.filter(
            id=draft["categoria"],
            negocio=factura.negocio,
            activo=True,
        ).first()
        if not categoria:
            has_error = True
            messages.error(request, "Debes seleccionar una categoría válida.")

        fecha_gasto_parsed = parse_date(draft["fecha_gasto"])
        if not fecha_gasto_parsed:
            has_error = True
            messages.error(request, "Debes indicar una fecha válida para el gasto.")

        metodos_pago_validos = {"", "EFECTIVO", "TRANSFERENCIA", "TARJETA"}
        if draft["metodo_pago"] not in metodos_pago_validos:
            has_error = True
            messages.error(request, "El método de pago seleccionado no es válido.")

        if len(draft["referencia_contable"]) > 80:
            has_error = True
            messages.error(request, "La referencia contable no puede exceder 80 caracteres.")

        tipo_cambio = None
        total_moneda_base = factura.total

        if (factura.moneda or "CRC") != factura.negocio.moneda_base:
            if not draft["tipo_cambio"]:
                has_error = True
                messages.error(
                    request,
                    f"Debes indicar tipo de cambio porque la factura está en {factura.moneda} y tu negocio usa {factura.negocio.moneda_base}.",
                )
            else:
                try:
                    tipo_cambio = Decimal(draft["tipo_cambio"])
                    if tipo_cambio <= 0:
                        raise InvalidOperation
                    total_moneda_base = (factura.total * tipo_cambio).quantize(Decimal("0.01"))
                except (InvalidOperation, ValueError, TypeError):
                    has_error = True
                    messages.error(request, "El tipo de cambio debe ser un número mayor que cero.")

        if not has_error:
            if not factura.proveedor_registrado:
                factura.proveedor_registrado = registrar_o_recuperar_proveedor(
                    factura.negocio,
                    factura.proveedor,
                    defaults={"email": factura.email_from or None},
                )
            Gasto.objects.create(
                negocio=factura.negocio,
                factura=factura,
                categoria=categoria,
                fecha_gasto=fecha_gasto_parsed,
                metodo_pago=draft["metodo_pago"] or None,
                referencia_contable=draft["referencia_contable"] or None,
                tipo_cambio=tipo_cambio,
                total_moneda_base=total_moneda_base,
                subtotal=factura.subtotal,
                iva=factura.iva,
                total=factura.total,
                notas=draft["notas"] or None,
                creado_por=request.user,
            )

            factura.estado = "registrada"
            factura.save(update_fields=["estado", "proveedor_registrado"])

            messages.success(request, "Gasto registrado correctamente.")
            return redirect("gastos:bandeja_facturas")

    return render(
        request,
        "gastos/registrar_gasto.html",
        {
            "factura": factura,
            "categorias": categorias,
            "draft": draft,
            "moneda_factura": (factura.moneda or "CRC"),
            "moneda_base_negocio": factura.negocio.moneda_base,
        },
    )


@login_required
def ver_gasto(request, gasto_id):
    negocio_id = request.session.get("negocio_activo_id")
    if not negocio_id:
        return redirect("core:home")

    gasto = get_object_or_404(
        Gasto.objects.select_related("factura", "categoria", "negocio"),
        id=gasto_id,
        negocio_id=negocio_id,
    )

    moneda_factura = (gasto.factura.moneda or "CRC").upper()
    moneda_base = (gasto.negocio.moneda_base or moneda_factura).upper()
    context = {
        "gasto": gasto,
        "moneda_factura": moneda_factura,
        "moneda_base": moneda_base,
        "simbolo_factura": _simbolo_moneda(moneda_factura),
        "simbolo_base": _simbolo_moneda(moneda_base),
        "mostrar_moneda_base": moneda_factura != moneda_base,
    }

    return render(request, "gastos/ver_factura.html", context)


@login_required
def listado_gastos(request):
    negocio_id = request.session.get("negocio_activo_id")
    if not negocio_id:
        return redirect("core:home")

    gastos = (
        Gasto.objects.filter(negocio_id=negocio_id)
        .select_related("categoria", "factura", "negocio")
        .order_by("-fecha_gasto")
    )

    q = (request.GET.get("q") or "").strip()
    categoria = (request.GET.get("categoria") or "").strip()
    metodo_pago = (request.GET.get("metodo_pago") or "").strip()
    fecha_desde = (request.GET.get("fecha_desde") or "").strip()
    fecha_hasta = (request.GET.get("fecha_hasta") or "").strip()

    if q:
        gastos = gastos.filter(
            Q(factura__proveedor__icontains=q) | Q(factura__numero_factura__icontains=q)
        )

    if categoria:
        if categoria.isdigit():
            gastos = gastos.filter(categoria_id=categoria)
        else:
            messages.error(request, "La categoría seleccionada no es válida.")
            categoria = ""

    metodos_pago_validos = {"EFECTIVO", "TRANSFERENCIA", "TARJETA"}
    if metodo_pago:
        if metodo_pago in metodos_pago_validos:
            gastos = gastos.filter(metodo_pago=metodo_pago)
        else:
            messages.error(request, "El método de pago seleccionado no es válido.")
            metodo_pago = ""

    fecha_desde_parsed = None
    fecha_hasta_parsed = None
    if fecha_desde:
        fecha_desde_parsed = parse_date(fecha_desde)
        if fecha_desde_parsed:
            gastos = gastos.filter(fecha_gasto__gte=fecha_desde_parsed)
        else:
            messages.error(request, "La fecha 'Desde' no tiene un formato válido.")
            fecha_desde = ""

    if fecha_hasta:
        fecha_hasta_parsed = parse_date(fecha_hasta)
        if fecha_hasta_parsed:
            gastos = gastos.filter(fecha_gasto__lte=fecha_hasta_parsed)
        else:
            messages.error(request, "La fecha 'Hasta' no tiene un formato válido.")
            fecha_hasta = ""

    if fecha_desde_parsed and fecha_hasta_parsed and fecha_desde_parsed > fecha_hasta_parsed:
        messages.error(request, "El rango de fechas es inválido: 'Desde' no puede ser mayor que 'Hasta'.")
        gastos = gastos.none()

    context = {
        "gastos": gastos,
        "categorias": CategoriaGasto.objects.filter(negocio_id=negocio_id, activo=True),
        "filtros": {
            "q": q,
            "categoria": categoria,
            "metodo_pago": metodo_pago,
            "fecha_desde": fecha_desde,
            "fecha_hasta": fecha_hasta,
        },
        "kpi": {
            "total": gastos.count(),
            "registrados": gastos.filter(estado="registrado").count(),
            "anulados": gastos.filter(estado="anulado").count(),
        },
    }

    return render(request, "gastos/listado_gastos.html", context)


@login_required
def anular_gasto(request, gasto_id):
    if request.method != "POST":
        messages.warning(request, "Acción inválida para anular un gasto.")
        return redirect("gastos:listado_gastos")

    negocio_id = request.session.get("negocio_activo_id")
    gasto = get_object_or_404(Gasto, id=gasto_id, negocio_id=negocio_id)

    if gasto.estado == "anulado":
        messages.info(request, "Este gasto ya se encuentra anulado.")
        return redirect("gastos:listado_gastos")

    gasto.estado = "anulado"
    gasto.save(update_fields=["estado"])
    messages.success(request, "Gasto anulado correctamente.")
    return redirect("gastos:listado_gastos")


@login_required
def editar_gasto(request, gasto_id):
    negocio_id = request.session.get("negocio_activo_id")
    gasto = get_object_or_404(Gasto, id=gasto_id, negocio_id=negocio_id)

    if gasto.estado != "registrado":
        messages.warning(request, "Solo puedes editar gastos en estado registrado.")
        return redirect("gastos:listado_gastos")

    moneda_factura = (gasto.factura.moneda or "CRC").upper()
    moneda_base = (gasto.negocio.moneda_base or moneda_factura).upper()

    draft = {
        "categoria": str(gasto.categoria_id or ""),
        "fecha_gasto": gasto.fecha_gasto.isoformat() if gasto.fecha_gasto else "",
        "metodo_pago": gasto.metodo_pago or "",
        "referencia_contable": gasto.referencia_contable or "",
        "tipo_cambio": str(gasto.tipo_cambio or ""),
        "notas": gasto.notas or "",
    }

    if request.method == "POST":
        draft.update(
            {
                "categoria": (request.POST.get("categoria") or "").strip(),
                "fecha_gasto": (request.POST.get("fecha_gasto") or "").strip(),
                "metodo_pago": (request.POST.get("metodo_pago") or "").strip(),
                "referencia_contable": (request.POST.get("referencia_contable") or "").strip(),
                "tipo_cambio": (request.POST.get("tipo_cambio") or "").strip(),
                "notas": (request.POST.get("notas") or "").strip(),
            }
        )

        has_error = False

        categoria = CategoriaGasto.objects.filter(
            id=draft["categoria"],
            negocio_id=negocio_id,
            activo=True,
        ).first()
        if not categoria:
            has_error = True
            messages.error(request, "Debes seleccionar una categoría válida.")

        fecha_gasto_parsed = parse_date(draft["fecha_gasto"])
        if not fecha_gasto_parsed:
            has_error = True
            messages.error(request, "Debes indicar una fecha válida para el gasto.")

        metodos_pago_validos = {"", "EFECTIVO", "TRANSFERENCIA", "TARJETA"}
        if draft["metodo_pago"] not in metodos_pago_validos:
            has_error = True
            messages.error(request, "El método de pago seleccionado no es válido.")

        if len(draft["referencia_contable"]) > 80:
            has_error = True
            messages.error(request, "La referencia contable no puede exceder 80 caracteres.")

        tipo_cambio = None
        total_moneda_base = gasto.total
        if moneda_factura != moneda_base:
            if not draft["tipo_cambio"]:
                has_error = True
                messages.error(
                    request,
                    f"Debes indicar tipo de cambio porque la factura está en {moneda_factura} y el negocio en {moneda_base}.",
                )
            else:
                try:
                    tipo_cambio = Decimal(draft["tipo_cambio"])
                    if tipo_cambio <= 0:
                        raise InvalidOperation
                    total_moneda_base = (gasto.total * tipo_cambio).quantize(Decimal("0.01"))
                except (InvalidOperation, ValueError, TypeError):
                    has_error = True
                    messages.error(request, "El tipo de cambio debe ser un número mayor que cero.")
        elif draft["tipo_cambio"]:
            try:
                tipo_cambio = Decimal(draft["tipo_cambio"])
            except (InvalidOperation, ValueError, TypeError):
                tipo_cambio = None

        if has_error:
            categorias = CategoriaGasto.objects.filter(negocio_id=gasto.negocio_id, activo=True)
            return render(
                request,
                "gastos/editar_gasto.html",
                {
                    "gasto": gasto,
                    "categorias": categorias,
                    "draft": draft,
                    "moneda_factura": moneda_factura,
                    "moneda_base": moneda_base,
                    "simbolo_factura": _simbolo_moneda(moneda_factura),
                    "simbolo_base": _simbolo_moneda(moneda_base),
                },
            )

        gasto.categoria = categoria
        gasto.fecha_gasto = fecha_gasto_parsed
        gasto.metodo_pago = draft["metodo_pago"] or None
        gasto.referencia_contable = draft["referencia_contable"] or None
        gasto.tipo_cambio = tipo_cambio if moneda_factura != moneda_base else None
        gasto.total_moneda_base = total_moneda_base
        gasto.notas = draft["notas"] or None
        gasto.save(
            update_fields=[
                "categoria",
                "fecha_gasto",
                "metodo_pago",
                "referencia_contable",
                "tipo_cambio",
                "total_moneda_base",
                "notas",
                "actualizado_en",
            ]
        )

        messages.success(request, "Gasto actualizado correctamente.")

        return redirect("gastos:listado_gastos")

    categorias = CategoriaGasto.objects.filter(negocio_id=gasto.negocio_id, activo=True)

    return render(
        request,
        "gastos/editar_gasto.html",
        {
            "gasto": gasto,
            "categorias": categorias,
            "draft": draft,
            "moneda_factura": moneda_factura,
            "moneda_base": moneda_base,
            "simbolo_factura": _simbolo_moneda(moneda_factura),
            "simbolo_base": _simbolo_moneda(moneda_base),
        },
    )
