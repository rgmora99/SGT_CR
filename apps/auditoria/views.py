from django.shortcuts import render
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, permission_required

@login_required
# @permission_required("contratos.view_contrato", raise_exception=True)
def mostrar_auditoria(request):
    return render(request, "gestion_contratos/contratos.html")

