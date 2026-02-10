from django.shortcuts import render
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, permission_required

@login_required
# @permission_required("contratos.add_contrato", raise_exception=True)
def crear_contrato(request):
    return render(request, "gestion_contratos/contratos/crear_contrato.html")

# @permission_required("contratos.view_contrato", raise_exception=True)
def listar_contratos(request):
    return render(request, "gestion_contratos/contratos/listar_contratos.html")

def contrato_ver(request):
    return render(request, "gestion_contratos/contratos/ver_contrato.html")

def contratos_facturas(request):
    return render(request, "contratos/facturas.html")

def contratos_observaciones(request):
    return render(request, "contratos/observaciones.html")

def contratos_recepciones(request):
    return render(request, "contratos/recepciones.html")