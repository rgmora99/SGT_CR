from django.shortcuts import render, get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Count, Q
from django.http import JsonResponse, HttpResponseBadRequest
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import AlertaForm
from .models import Alerta

@login_required
# @permission_required("contratos.add_contrato", raise_exception=True)
def crear_alerta(request):
    if request.method == "POST":
        form = AlertaForm(request.POST)
        if form.is_valid():
            alerta = form.save(commit=False)
            alerta.creado_por = request.user
            alerta.save()
            return redirect("alertas:listar")
    else:
        form = AlertaForm()
    return render(request, "alertas/crear_alerta.html", {"form": form})

# @permission_required("contratos.view_contrato", raise_exception=True)
from django.shortcuts import render
from django.utils import timezone
from .models import Alerta, EstadoAlerta, TipoAlerta

@login_required
def listar_alertas(request):

    hoy = timezone.localdate()

    # =========================
    # Estados base
    # =========================
    estado_pendiente = EstadoAlerta.objects.get(codigo="PENDIENTE")
    estado_atendida = EstadoAlerta.objects.get(codigo="ATENDIDA")

    # =========================
    # KPIs
    # =========================
    kpi = {
        "proximos": Alerta.objects.filter(
            fecha_aviso__gte=hoy,
            fecha_aviso__lte=hoy + timezone.timedelta(days=7),
            estado=estado_pendiente
        ).count(),

        "vencidos": Alerta.objects.filter(
            fecha_aviso__lt=hoy,
            estado=estado_pendiente
        ).count(),

        "facturas_pend": Alerta.objects.filter(
            tipo__codigo="FACTURA",
            estado=estado_pendiente
        ).count(),

        "atendidas": Alerta.objects.filter(
            estado=estado_atendida
        ).count(),
    }

    # =========================
    # Filtros GET
    # =========================
    q = request.GET.get("q", "")
    tipo = request.GET.get("tipo", "")
    estado = request.GET.get("estado", "")
    desde = request.GET.get("desde", "")
    hasta = request.GET.get("hasta", "")

    alertas = Alerta.objects.select_related(
        "tipo", "estado", "prioridad", "medio"
    )

    if q:
        alertas = alertas.filter(
            Q(descripcion__icontains=q) |
            Q(contrato__numero__icontains=q)
        )

    if tipo:
        alertas = alertas.filter(tipo__codigo=tipo)

    if estado:
        alertas = alertas.filter(estado__codigo=estado)

    if desde:
        alertas = alertas.filter(fecha_aviso__gte=desde)

    if hasta:
        alertas = alertas.filter(fecha_aviso__lte=hasta)

    # =========================
    # Catálogos para filtros
    # =========================
    tipos = TipoAlerta.objects.values_list("codigo", "descripcion")
    estados = EstadoAlerta.objects.values_list("codigo", "codigo")

    context = {
        "alertas": alertas.order_by("-fecha_aviso"),
        "kpi": kpi,
        "tipos": tipos,
        "estados": estados,
        "filtros": {
            "q": q,
            "tipo": tipo,
            "estado": estado,
            "desde": desde,
            "hasta": hasta,
        }
    }

    return render(request, "alertas/listar_alertas.html", context)


def ver_alerta(request):
    return render(request, "alertas/ver_alerta.html")

def editar_alerta(request):
    return render(request, "alertas/editar_alerta.html")


@login_required
@require_POST
def marcar_atendida(request, pk):
    alerta = get_object_or_404(Alerta, pk=pk)
    alerta.estado = Alerta.Estado.ATENDIDA
    alerta.save(update_fields=["estado"])
    return JsonResponse({"ok": True, "estado": "ATENDIDA"})


@login_required
@require_POST
def eliminar_alerta(request, pk):
    alerta = get_object_or_404(Alerta, pk=pk)
    alerta.delete()
    return JsonResponse({"ok": True})
