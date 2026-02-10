from django.shortcuts import render, get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Count, Q
from django.http import JsonResponse, HttpResponseBadRequest
from django.utils import timezone
from django.views.decorators.http import require_POST


@login_required
# @permission_required("contratos.add_contrato", raise_exception=True)
def crear_venta(request):
    return render(request, "ventas/crear_venta.html")

# @permission_required("contratos.view_contrato", raise_exception=True)
from django.shortcuts import render
from django.utils import timezone

@login_required
def listar_venta(request):
    return render(request, "ventas/listar_ventas.html")


