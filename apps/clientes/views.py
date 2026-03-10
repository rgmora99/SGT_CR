from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import ProtectedError
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ClienteForm
from .models import Cliente


@login_required
def cliente_listar(request):
    q = request.GET.get("q", "").strip()
    estado = request.GET.get("estado", "").strip()

    clientes = Cliente.objects.all()
    if q:
        clientes = clientes.filter(
            Q(nombre__icontains=q)
            | Q(identificacion__icontains=q)
            | Q(correo_electronico__icontains=q)
            | Q(telefono__icontains=q)
        )
    if estado:
        clientes = clientes.filter(estado=estado)

    paginator = Paginator(clientes, 10)
    page_obj = paginator.get_page(request.GET.get("page"))

    context = {
        "page_obj": page_obj,
        "filtros": {"q": q, "estado": estado},
        "kpi": {
            "total": Cliente.objects.count(),
            "activos": Cliente.objects.filter(estado=Cliente.Estado.ACTIVO).count(),
            "inactivos": Cliente.objects.filter(estado=Cliente.Estado.INACTIVO).count(),
            "visibles": page_obj.paginator.count,
        },
        "estado_choices": Cliente.Estado.choices,
    }
    return render(request, "clientes/lista.html", context)


@login_required
def cliente_crear(request):
    form = ClienteForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Cliente creado correctamente.")
        return redirect("clientes:listar")
    return render(request, "clientes/form.html", {"form": form, "modo": "crear"})


@login_required
def cliente_detalle(request, cliente_id):
    cliente = get_object_or_404(Cliente, id=cliente_id)
    return render(request, "clientes/detalle.html", {"cliente": cliente})


@login_required
def cliente_editar(request, cliente_id):
    cliente = get_object_or_404(Cliente, id=cliente_id)
    form = ClienteForm(request.POST or None, instance=cliente)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Cliente actualizado correctamente.")
        return redirect("clientes:listar")
    return render(request, "clientes/form.html", {"form": form, "modo": "editar", "cliente": cliente})


@login_required
def cliente_eliminar(request, cliente_id):
    cliente = get_object_or_404(Cliente, id=cliente_id)
    if request.method == "POST":
        try:
            cliente.delete()
            messages.success(request, "Cliente eliminado correctamente.")
        except ProtectedError:
            messages.error(
                request,
                "No se puede eliminar el cliente porque tiene movimientos asociados. "
                "Desactívelo o elimine primero sus registros relacionados.",
            )
    return redirect("clientes:listar")


@login_required
def validar_identificacion(request):
    identificacion = (request.GET.get("identificacion") or "").strip().upper().replace(" ", "")
    cliente_id = request.GET.get("cliente_id")

    queryset = Cliente.objects.filter(identificacion=identificacion)
    if cliente_id and str(cliente_id).isdigit():
        queryset = queryset.exclude(pk=int(cliente_id))

    existe = bool(identificacion) and queryset.exists()
    return JsonResponse({"duplicado": existe})
