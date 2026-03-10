import json
from urllib.error import URLError
from urllib.request import urlopen

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST

from .forms import DetalleIngresoFormSet, IngresoForm
from .models import CategoriaIngreso, Ingreso
from .services.bootstrap import asegurar_categorias_base, asegurar_productos_base
from .services.calculos import calcular_totales_ingreso


def _negocio_id(request):
    return request.session.get("negocio_activo_id")


def _preparar_catalogos(negocio_id):
    asegurar_categorias_base(negocio_id)
    asegurar_productos_base(negocio_id)


@login_required
def listado_ingresos(request):
    negocio_id = _negocio_id(request)
    if not negocio_id:
        messages.warning(request, "Debes seleccionar un negocio para continuar.")
        return redirect("core:home")

    _preparar_catalogos(negocio_id)

    ingresos = Ingreso.objects.filter(negocio_id=negocio_id).select_related("cliente", "categoria")

    q = (request.GET.get("q") or "").strip()
    estado = (request.GET.get("estado") or "").strip()
    categoria_id = (request.GET.get("categoria") or "").strip()

    if q:
        ingresos = ingresos.filter(Q(cliente__nombre__icontains=q) | Q(consecutivo__icontains=q))
    if estado:
        ingresos = ingresos.filter(estado=estado)
    if categoria_id.isdigit():
        ingresos = ingresos.filter(categoria_id=categoria_id)

    resumen = ingresos.aggregate(total_monto=Sum("total"))

    return render(
        request,
        "ingresos/listado_ingresos.html",
        {
            "ingresos": ingresos,
            "categorias": CategoriaIngreso.objects.filter(negocio_id=negocio_id, activo=True),
            "filtros": {"q": q, "estado": estado, "categoria": categoria_id},
            "kpi": {
                "total_registros": ingresos.count(),
                "confirmados": ingresos.filter(estado=Ingreso.Estado.CONFIRMADO).count(),
                "monto_total": resumen["total_monto"] or 0,
            },
        },
    )


@login_required
def crear_ingreso(request):
    negocio_id = _negocio_id(request)
    if not negocio_id:
        return redirect("core:home")

    _preparar_catalogos(negocio_id)

    consecutivo_sugerido = Ingreso.generar_consecutivo(negocio_id=negocio_id, year=timezone.now().year)

    if request.method == "POST":
        form = IngresoForm(request.POST, negocio_id=negocio_id, consecutivo_sugerido=consecutivo_sugerido)
        formset = DetalleIngresoFormSet(request.POST, negocio_id=negocio_id)
        if form.is_valid() and formset.is_valid():
            ingreso = form.save(commit=False)
            ingreso.negocio_id = negocio_id
            ingreso.creado_por = request.user
            ingreso.consecutivo = Ingreso.generar_consecutivo(negocio_id=negocio_id, year=ingreso.fecha_ingreso.year)
            ingreso.save()

            detalles = formset.save(commit=False)
            for detalle in detalles:
                detalle.ingreso = ingreso
                if detalle.producto and not detalle.descripcion:
                    detalle.descripcion = detalle.producto.nombre
                if detalle.producto and (not detalle.precio_unitario or detalle.precio_unitario == 0):
                    detalle.precio_unitario = detalle.producto.precio_base
                detalle.save()

            for obj in formset.deleted_objects:
                obj.delete()

            subtotal, iva, total = calcular_totales_ingreso(ingreso.detalles.all())
            ingreso.subtotal = subtotal
            ingreso.iva = iva
            ingreso.total = total
            ingreso.save(update_fields=["subtotal", "iva", "total"])
            messages.success(request, f"Ingreso {ingreso.consecutivo} registrado correctamente.")
            return redirect("ingresos:ver_ingreso", ingreso_id=ingreso.id)

        messages.error(request, "No se pudo guardar el ingreso. Revisa los campos requeridos.")
    else:
        form = IngresoForm(negocio_id=negocio_id, consecutivo_sugerido=consecutivo_sugerido)
        formset = DetalleIngresoFormSet(negocio_id=negocio_id)

    return render(request, "ingresos/form_ingreso.html", {"form": form, "formset": formset, "edicion": False})


@login_required
def editar_ingreso(request, ingreso_id):
    negocio_id = _negocio_id(request)
    ingreso = get_object_or_404(Ingreso, id=ingreso_id, negocio_id=negocio_id)

    _preparar_catalogos(negocio_id)

    if request.method == "POST":
        form = IngresoForm(request.POST, instance=ingreso, negocio_id=negocio_id)
        formset = DetalleIngresoFormSet(request.POST, instance=ingreso, negocio_id=negocio_id)
        if form.is_valid() and formset.is_valid():
            ingreso = form.save(commit=False)
            ingreso.consecutivo = ingreso.__class__.objects.get(pk=ingreso.pk).consecutivo
            ingreso.save()
            detalles = formset.save(commit=False)
            for detalle in detalles:
                detalle.ingreso = ingreso
                if detalle.producto and not detalle.descripcion:
                    detalle.descripcion = detalle.producto.nombre
                if detalle.producto and (not detalle.precio_unitario or detalle.precio_unitario == 0):
                    detalle.precio_unitario = detalle.producto.precio_base
                detalle.save()

            for obj in formset.deleted_objects:
                obj.delete()

            subtotal, iva, total = calcular_totales_ingreso(ingreso.detalles.all())
            ingreso.subtotal = subtotal
            ingreso.iva = iva
            ingreso.total = total
            ingreso.save(update_fields=["subtotal", "iva", "total", "actualizado_en"])
            messages.success(request, "Ingreso actualizado correctamente.")
            return redirect("ingresos:ver_ingreso", ingreso_id=ingreso.id)

        messages.error(request, "No se pudo actualizar el ingreso. Revisa la información ingresada.")
    else:
        form = IngresoForm(instance=ingreso, negocio_id=negocio_id)
        formset = DetalleIngresoFormSet(instance=ingreso, negocio_id=negocio_id)

    return render(request, "ingresos/form_ingreso.html", {"form": form, "formset": formset, "ingreso": ingreso, "edicion": True})


@login_required
def ver_ingreso(request, ingreso_id):
    negocio_id = _negocio_id(request)
    ingreso = get_object_or_404(Ingreso.objects.select_related("cliente", "categoria"), id=ingreso_id, negocio_id=negocio_id)
    return render(request, "ingresos/ver_ingreso.html", {"ingreso": ingreso})


@require_POST
@login_required
def anular_ingreso(request, ingreso_id):
    negocio_id = _negocio_id(request)
    ingreso = get_object_or_404(Ingreso, id=ingreso_id, negocio_id=negocio_id)
    ingreso.estado = Ingreso.Estado.ANULADO
    ingreso.save(update_fields=["estado", "actualizado_en"])
    messages.success(request, "Ingreso anulado correctamente.")
    return redirect("ingresos:listado")


def _extraer_tipo_cambio(payload):
    if not isinstance(payload, dict):
        return None, None

    if isinstance(payload.get("venta"), dict) and payload["venta"].get("valor"):
        return float(payload["venta"]["valor"]), "hacienda"

    if payload.get("dolar") and isinstance(payload.get("dolar"), dict):
        valor_venta = payload["dolar"].get("venta")
        if valor_venta:
            return float(valor_venta), "bccr"

    rates = payload.get("rates")
    if isinstance(rates, dict) and rates.get("CRC"):
        return float(rates["CRC"]), "fx"

    return None, None


@require_GET
@login_required
def tipo_cambio_bcr(request):
    """
    Endpoint de consulta de tipo de cambio USD->CRC con múltiples fuentes.
    """
    urls = [
        "https://api.hacienda.go.cr/indicadores/tc",
        "https://api.exchangerate.host/latest?base=USD&symbols=CRC",
        "https://api.frankfurter.app/latest?from=USD&to=CRC",
        "https://open.er-api.com/v6/latest/USD",
    ]

    for url in urls:
        try:
            with urlopen(url, timeout=8) as response:
                payload = json.loads(response.read().decode("utf-8"))
            tipo_cambio, fuente = _extraer_tipo_cambio(payload)
            if tipo_cambio:
                return JsonResponse({"ok": True, "fuente": fuente, "tipo_cambio": tipo_cambio})
        except (URLError, TimeoutError, ValueError, json.JSONDecodeError):
            continue

    return JsonResponse({"ok": False, "error": "No se pudo obtener tipo de cambio en este momento."}, status=503)
