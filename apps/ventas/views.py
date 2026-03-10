from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Sum
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404, redirect, render

from .forms import (
    AlmacenForm,
    CategoriaItemForm,
    ImpuestoForm,
    ProductoServicioForm,
    UnidadMedidaForm,
)
from .models import Almacen, CategoriaItem, Existencia, FacturaVenta, Impuesto, ProductoServicio, UnidadMedida


def _negocio_id(request):
    return request.session.get("negocio_activo_id")


@login_required
def listar_venta(request):
    return render(request, "ventas/listar_ventas.html")


@login_required
def crear_venta(request):
    return render(request, "ventas/crear_venta.html")


@login_required
def inventario_dashboard(request):
    negocio_id = _negocio_id(request)
    if not negocio_id:
        messages.warning(request, "Debes seleccionar un negocio para gestionar inventario.")
        return redirect("core:home")

    productos = ProductoServicio.objects.filter(negocio_id=negocio_id)
    almacenes = Almacen.objects.filter(negocio_id=negocio_id)
    facturas_emitidas = FacturaVenta.objects.filter(negocio_id=negocio_id, estado=FacturaVenta.Estado.EMITIDA).count()
    total_stock = Existencia.objects.filter(almacen__negocio_id=negocio_id).aggregate(
        total=Coalesce(Sum("cantidad_disponible"), 0)
    )["total"]

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
