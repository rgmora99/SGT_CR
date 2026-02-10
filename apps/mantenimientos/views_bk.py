from django.shortcuts import render
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, permission_required

@login_required
# @permission_required("contratos.add_contrato", raise_exception=True)
def contrato_nuevo(request):
    return render(request, "gestion_contratos/contrato_nuevo.html")

# @permission_required("contratos.view_contrato", raise_exception=True)
def contratos_listar(request):
    return render(request, "gestion_contratos/contratos.html")

def contrato_ver(request):
    return render(request, "gestion_contratos/contratos.html")

def contratos_prorrogas(request):
    return render(request, "contratos/prorrogas.html")

def contratos_garantias(request):
    return render(request, "contratos/garantias.html")

def contratos_facturas(request):
    return render(request, "contratos/facturas.html")

def contratos_observaciones(request):
    return render(request, "contratos/observaciones.html")

def contratos_ordenes(request):
    return render(request, "contratos/ordenes.html")

def contratos_recepciones(request):
    return render(request, "contratos/recepciones.html")