import csv
from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.utils import timezone

from apps.fiscal.models import CierreFiscalPeriodo
from apps.fiscal.services import calcular_resumen_fiscal


@login_required
def dashboard_fiscal(request):
    negocio_id = request.session.get("negocio_activo_id")
    if not negocio_id:
        messages.warning(request, "Debes seleccionar un negocio para ver el módulo fiscal.")
        return redirect("core:home")

    anio = timezone.now().year
    mes = timezone.now().month
    tasa_renta = Decimal("0.30")

    if request.method == "GET":
        anio = int(request.GET.get("anio") or anio)
        mes_raw = request.GET.get("mes")
        mes = int(mes_raw) if mes_raw else None
        tasa_raw = request.GET.get("tasa_renta", "30")
        try:
            tasa_renta = Decimal(tasa_raw) / Decimal("100")
        except (InvalidOperation, ValueError, TypeError):
            tasa_renta = Decimal("0.30")
            messages.error(request, "La tasa de renta no es válida, se aplicó 30%.")

    resumen = calcular_resumen_fiscal(negocio_id=negocio_id, anio=anio, mes=mes, tasa_renta=tasa_renta)

    cierre = CierreFiscalPeriodo.objects.filter(
        negocio_id=negocio_id,
        tipo=CierreFiscalPeriodo.Tipo.MENSUAL if mes else CierreFiscalPeriodo.Tipo.ANUAL,
        anio=anio,
        mes=mes,
    ).first()

    if request.method == "POST":
        accion = request.POST.get("accion")
        if accion == "cerrar":
            cierre, _ = CierreFiscalPeriodo.objects.update_or_create(
                negocio_id=negocio_id,
                tipo=CierreFiscalPeriodo.Tipo.MENSUAL if mes else CierreFiscalPeriodo.Tipo.ANUAL,
                anio=anio,
                mes=mes,
                defaults={
                    **resumen,
                    "estado": CierreFiscalPeriodo.Estado.CERRADO,
                    "cerrado_en": timezone.now(),
                    "observaciones": request.POST.get("observaciones", ""),
                },
            )
            messages.success(request, "Período fiscal cerrado correctamente.")
            return redirect(f"{request.path}?anio={anio}&mes={mes or ''}&tasa_renta={(tasa_renta*100)}")

    context = {
        "resumen": resumen,
        "anio": anio,
        "mes": mes,
        "tasa_renta_porcentaje": (tasa_renta * 100),
        "cierre": cierre,
    }
    return render(request, "fiscal/dashboard.html", context)


@login_required
def exportar_borrador_csv(request):
    negocio_id = request.session.get("negocio_activo_id")
    if not negocio_id:
        return redirect("core:home")

    anio = int(request.GET.get("anio") or timezone.now().year)
    mes_raw = request.GET.get("mes")
    mes = int(mes_raw) if mes_raw else None
    tasa_raw = request.GET.get("tasa_renta", "30")

    try:
        tasa_renta = Decimal(tasa_raw) / Decimal("100")
    except (InvalidOperation, ValueError, TypeError):
        tasa_renta = Decimal("0.30")

    resumen = calcular_resumen_fiscal(negocio_id=negocio_id, anio=anio, mes=mes, tasa_renta=tasa_renta)

    response = HttpResponse(content_type="text/csv")
    periodo = f"{anio}-{str(mes).zfill(2)}" if mes else str(anio)
    response["Content-Disposition"] = f'attachment; filename="borrador_fiscal_{periodo}.csv"'

    writer = csv.writer(response)
    writer.writerow(["Campo", "Valor"])
    writer.writerow(["Periodo", periodo])
    writer.writerow(["Compras gravadas", resumen["compras_gravadas"]])
    writer.writerow(["Compras exentas", resumen["compras_exentas"]])
    writer.writerow(["Crédito fiscal IVA", resumen["credito_fiscal"]])
    writer.writerow(["Ventas gravadas", resumen["ventas_gravadas"]])
    writer.writerow(["Ventas exentas", resumen["ventas_exentas"]])
    writer.writerow(["Débito fiscal IVA", resumen["debito_fiscal"]])
    writer.writerow(["IVA por pagar", resumen["iva_por_pagar"]])
    writer.writerow(["Utilidad proyectada", resumen["utilidad_proyectada"]])
    writer.writerow(["Impuesto renta proyectado", resumen["impuesto_renta_proyectado"]])

    return response
