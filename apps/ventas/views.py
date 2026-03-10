from decimal import Decimal
from datetime import date
import re

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db import transaction
from django.db.models import DecimalField, Q, Sum, Value
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404, redirect, render

from apps.clientes.models import Cliente

from .forms import (
    AlmacenForm,
    CategoriaItemForm,
    ImpuestoForm,
    ProductoServicioForm,
    UnidadMedidaForm,
)
from .models import (
    Almacen,
    CategoriaItem,
    Existencia,
    FacturaVenta,
    Impuesto,
    LineaFacturaVenta,
    ProductoServicio,
    UnidadMedida,
)
from .services import emitir_factura


def _negocio_id(request):
    return request.session.get("negocio_activo_id")


CONSECUTIVO_REGEX_CR = re.compile(r"^\d{20}$")


def _generar_consecutivo_cr(negocio_id):
    prefijo = "0010000101"  # 001 sucursal + 00001 punto venta + 01 factura electrónica
    secuencia = 1

    for consecutivo in FacturaVenta.objects.filter(negocio_id=negocio_id).order_by("-id").values_list("consecutivo", flat=True)[:500]:
        if not CONSECUTIVO_REGEX_CR.match(consecutivo or ""):
            continue
        if not consecutivo.startswith(prefijo):
            continue
        secuencia = int(consecutivo[-10:]) + 1
        break

    return f"{prefijo}{secuencia:010d}"


@login_required
def listar_venta(request):
    negocio_id = _negocio_id(request)
    facturas = FacturaVenta.objects.filter(negocio_id=negocio_id).select_related("cliente", "almacen").order_by("-fecha_emision", "-id")
    return render(request, "ventas/facturas_lista.html", {"facturas": facturas})


@login_required
def crear_venta(request):
    negocio_id = _negocio_id(request)
    if not negocio_id:
        messages.warning(request, "Debes seleccionar un negocio para continuar.")
        return redirect("core:home")

    clientes = Cliente.objects.all().order_by("nombre")
    almacenes = Almacen.objects.filter(negocio_id=negocio_id, activo=True).order_by("nombre")
    productos = ProductoServicio.objects.filter(negocio_id=negocio_id, activo=True).select_related("impuesto").order_by("nombre")

    consecutivo_sugerido = _generar_consecutivo_cr(negocio_id)

    if request.method == "POST":
        cliente_id = request.POST.get("cliente")
        almacen_id = request.POST.get("almacen") or None
        producto_id = request.POST.get("producto")
        cantidad_raw = request.POST.get("cantidad")
        descuento_raw = request.POST.get("porcentaje_descuento") or "0"
        consecutivo = _generar_consecutivo_cr(negocio_id)
        moneda = (request.POST.get("moneda") or "CRC").strip().upper()
        tipo_cambio_raw = (request.POST.get("tipo_cambio") or "").strip()
        fecha_emision_raw = (request.POST.get("fecha_emision") or "").strip()
        fecha_vencimiento_raw = (request.POST.get("fecha_vencimiento") or "").strip()

        if not cliente_id or not producto_id:
            messages.error(request, "Debes seleccionar cliente y producto.")
            return redirect("ventas:crear")

        if moneda not in {"CRC", "USD"}:
            messages.error(request, "La moneda seleccionada no es válida.")
            return redirect("ventas:crear")

        try:
            cantidad = Decimal(cantidad_raw)
            descuento = Decimal(descuento_raw)
            if cantidad <= 0:
                raise ValueError
            if descuento < 0 or descuento > 100:
                raise ValueError
        except Exception:
            messages.error(request, "Cantidad o descuento inválidos.")
            return redirect("ventas:crear")

        try:
            fecha_emision = date.fromisoformat(fecha_emision_raw)
        except ValueError:
            messages.error(request, "La fecha de emisión no es válida.")
            return redirect("ventas:crear")

        if fecha_emision > date.today():
            messages.error(request, "La fecha de emisión no puede ser futura.")
            return redirect("ventas:crear")

        fecha_vencimiento = None
        if fecha_vencimiento_raw:
            try:
                fecha_vencimiento = date.fromisoformat(fecha_vencimiento_raw)
            except ValueError:
                messages.error(request, "La fecha de vencimiento no es válida.")
                return redirect("ventas:crear")

            if fecha_vencimiento < fecha_emision:
                messages.error(request, "La fecha de vencimiento no puede ser menor a la fecha de emisión.")
                return redirect("ventas:crear")

        tipo_cambio = None
        if moneda == "USD":
            try:
                tipo_cambio = Decimal(tipo_cambio_raw)
                if tipo_cambio <= 0:
                    raise ValueError
            except Exception:
                messages.error(request, "Para facturas en USD debes indicar un tipo de cambio mayor a cero.")
                return redirect("ventas:crear")

        cliente = get_object_or_404(Cliente, pk=cliente_id)
        producto = get_object_or_404(ProductoServicio, pk=producto_id, negocio_id=negocio_id, activo=True)

        if producto.maneja_inventario and not almacen_id:
            messages.error(request, "Selecciona almacén para productos con inventario.")
            return redirect("ventas:crear")

        if request.POST.get("emitir") == "SI" and producto.maneja_inventario:
            existencia = Existencia.objects.filter(almacen_id=almacen_id, producto=producto).first()
            stock_libre = existencia.cantidad_libre if existencia else Decimal("0.000")
            if stock_libre < cantidad:
                messages.error(
                    request,
                    f"Stock insuficiente para {producto.nombre}. Disponible: {stock_libre}. Solicitado: {cantidad}.",
                )
                return redirect("ventas:crear")

        if FacturaVenta.objects.filter(negocio_id=negocio_id, consecutivo__iexact=consecutivo).exists():
            messages.error(request, "El consecutivo ya existe para este negocio.")
            return redirect("ventas:crear")

        with transaction.atomic():
            factura = FacturaVenta.objects.create(
                negocio_id=negocio_id,
                cliente=cliente,
                almacen_id=almacen_id,
                consecutivo=consecutivo.upper(),
                fecha_emision=fecha_emision,
                fecha_vencimiento=fecha_vencimiento,
                moneda=moneda,
                tipo_cambio=tipo_cambio,
                creado_por=request.user,
                notas=request.POST.get("notas") or "",
            )

            LineaFacturaVenta.objects.create(
                factura=factura,
                producto=producto,
                descripcion=producto.nombre,
                cantidad=cantidad,
                precio_unitario=producto.precio_venta,
                porcentaje_descuento=descuento,
                porcentaje_impuesto=producto.impuesto.porcentaje if producto.impuesto else Decimal("0.00"),
            )

            if request.POST.get("emitir") == "SI":
                try:
                    emitir_factura(factura, user=request.user)
                except Exception as exc:
                    messages.error(request, f"Factura guardada, pero no se pudo emitir: {exc}")
                    return redirect("ventas:listar")

        messages.success(request, "Factura creada correctamente.")
        return redirect("ventas:listar")

    context = {
        "clientes": clientes,
        "almacenes": almacenes,
        "productos": productos,
        "consecutivo_sugerido": consecutivo_sugerido,
    }
    return render(request, "ventas/factura_simple_form.html", context)


@login_required
def stock_disponible_api(request):
    negocio_id = _negocio_id(request)
    producto_id = request.GET.get("producto_id")
    almacen_id = request.GET.get("almacen_id")

    if not negocio_id or not producto_id:
        return JsonResponse({"ok": False, "error": "Parámetros incompletos."}, status=400)

    producto = get_object_or_404(ProductoServicio, pk=producto_id, negocio_id=negocio_id)
    if not producto.maneja_inventario:
        return JsonResponse({"ok": True, "maneja_inventario": False, "stock_libre": "0.000"})

    if not almacen_id:
        return JsonResponse({"ok": False, "error": "Debes seleccionar almacén."}, status=400)

    existencia = Existencia.objects.filter(almacen_id=almacen_id, producto=producto).first()
    stock_libre = existencia.cantidad_libre if existencia else Decimal("0.000")
    return JsonResponse(
        {
            "ok": True,
            "maneja_inventario": True,
            "stock_libre": f"{stock_libre:.3f}",
            "producto": producto.nombre,
        }
    )


@login_required
def emitir_venta(request, factura_id):
    negocio_id = _negocio_id(request)
    factura = get_object_or_404(FacturaVenta, pk=factura_id, negocio_id=negocio_id)
    try:
        emitir_factura(factura, user=request.user)
        messages.success(request, "Factura emitida y stock actualizado.")
    except Exception as exc:
        messages.error(request, f"No se pudo emitir la factura: {exc}")
    return redirect("ventas:listar")


@login_required
def inventario_dashboard(request):
    negocio_id = _negocio_id(request)
    if not negocio_id:
        messages.warning(request, "Debes seleccionar un negocio para gestionar inventario.")
        return redirect("core:home")

    productos = ProductoServicio.objects.filter(negocio_id=negocio_id)
    almacenes = Almacen.objects.filter(negocio_id=negocio_id)
    facturas_emitidas = FacturaVenta.objects.filter(negocio_id=negocio_id, estado=FacturaVenta.Estado.EMITIDA).count()
    total_stock = (
        Existencia.objects.filter(almacen__negocio_id=negocio_id)
        .aggregate(
            total=Coalesce(
                Sum("cantidad_disponible"),
                Value(Decimal("0.000"), output_field=DecimalField(max_digits=12, decimal_places=3)),
            )
        )
        .get("total")
    )

    return render(
        request,
        "ventas/inventario_dashboard.html",
        {
            "kpi": {
                "productos": productos.count(),
                "servicios": productos.filter(tipo=ProductoServicio.Tipo.SERVICIO).count(),
                "almacenes": almacenes.count(),
                "facturas_emitidas": facturas_emitidas,
                "stock_total": total_stock,
            }
        },
    )


@login_required
def listar_productos(request):
    negocio_id = _negocio_id(request)
    if not negocio_id:
        messages.warning(request, "Debes seleccionar un negocio para continuar.")
        return redirect("core:home")

    q = (request.GET.get("q") or "").strip()
    productos = ProductoServicio.objects.filter(negocio_id=negocio_id).select_related(
        "categoria", "unidad_medida", "impuesto"
    )
    if q:
        productos = productos.filter(Q(nombre__icontains=q) | Q(codigo__icontains=q))

    return render(
        request,
        "ventas/productos_lista.html",
        {"productos": productos.order_by("nombre"), "q": q},
    )


@login_required
def crear_producto(request):
    negocio_id = _negocio_id(request)
    if not negocio_id:
        messages.warning(request, "Debes seleccionar un negocio para continuar.")
        return redirect("core:home")

    form = ProductoServicioForm(request.POST or None, negocio_id=negocio_id)
    if request.method == "POST" and form.is_valid():
        producto = form.save(commit=False)
        producto.negocio_id = negocio_id
        producto.save()
        messages.success(request, "Producto/servicio creado correctamente.")
        return redirect("ventas:productos")

    return render(request, "ventas/producto_form.html", {"form": form, "modo": "crear"})


@login_required
def editar_producto(request, producto_id):
    negocio_id = _negocio_id(request)
    producto = get_object_or_404(ProductoServicio, pk=producto_id, negocio_id=negocio_id)

    form = ProductoServicioForm(request.POST or None, instance=producto, negocio_id=negocio_id)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Producto/servicio actualizado correctamente.")
        return redirect("ventas:productos")

    return render(request, "ventas/producto_form.html", {"form": form, "modo": "editar", "producto": producto})


@login_required
def mantenimiento_catalogos(request):
    negocio_id = _negocio_id(request)
    if not negocio_id:
        messages.warning(request, "Debes seleccionar un negocio para continuar.")
        return redirect("core:home")

    categoria_form = CategoriaItemForm(prefix="cat", negocio_id=negocio_id)
    unidad_form = UnidadMedidaForm(prefix="uni")
    impuesto_form = ImpuestoForm(prefix="imp", negocio_id=negocio_id)
    almacen_form = AlmacenForm(prefix="alm", negocio_id=negocio_id)

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "categoria":
            categoria_form = CategoriaItemForm(request.POST, prefix="cat", negocio_id=negocio_id)
            if categoria_form.is_valid():
                obj = categoria_form.save(commit=False)
                obj.negocio_id = negocio_id
                obj.save()
                messages.success(request, "Categoría registrada correctamente.")
                return redirect("ventas:catalogos")
            messages.error(request, "No se pudo registrar la categoría. Revisa los campos.")

        elif action == "unidad":
            unidad_form = UnidadMedidaForm(request.POST, prefix="uni")
            if unidad_form.is_valid():
                unidad_form.save()
                messages.success(request, "Unidad registrada correctamente.")
                return redirect("ventas:catalogos")
            messages.error(request, "No se pudo registrar la unidad de medida.")

        elif action == "impuesto":
            impuesto_form = ImpuestoForm(request.POST, prefix="imp", negocio_id=negocio_id)
            if impuesto_form.is_valid():
                obj = impuesto_form.save(commit=False)
                obj.negocio_id = negocio_id
                obj.save()
                messages.success(request, "Impuesto registrado correctamente.")
                return redirect("ventas:catalogos")
            messages.error(request, "No se pudo registrar el impuesto.")

        elif action == "almacen":
            almacen_form = AlmacenForm(request.POST, prefix="alm", negocio_id=negocio_id)
            if almacen_form.is_valid():
                obj = almacen_form.save(commit=False)
                obj.negocio_id = negocio_id
                obj.save()
                messages.success(request, "Almacén registrado correctamente.")
                return redirect("ventas:catalogos")
            messages.error(request, "No se pudo registrar el almacén.")

    context = {
        "categoria_form": categoria_form,
        "unidad_form": unidad_form,
        "impuesto_form": impuesto_form,
        "almacen_form": almacen_form,
        "categorias": CategoriaItem.objects.filter(negocio_id=negocio_id).order_by("nombre"),
        "unidades": UnidadMedida.objects.all().order_by("nombre"),
        "impuestos": Impuesto.objects.filter(negocio_id=negocio_id).order_by("nombre"),
        "almacenes": Almacen.objects.filter(negocio_id=negocio_id).order_by("nombre"),
    }
    return render(request, "ventas/catalogos_mantenimiento.html", context)
