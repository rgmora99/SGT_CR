from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.http import JsonResponse
from django.utils.timezone import now
from django.views.decorators.http import require_POST

from apps.gastos.models import ConfigCorreoFactura
from apps.gastos.services.sync_facturas import sync_facturas


@login_required
@require_POST
def sync_facturas_ajax(request):
    """
    Sincroniza facturas no leídas del año actual para el negocio activo.
    """

    year_actual = now().year
    negocio_id = request.session.get("negocio_activo_id")

    if not negocio_id:
        return JsonResponse(
            {"ok": False, "error": "No hay negocio activo en sesión."},
            status=400,
        )

    if not ConfigCorreoFactura.objects.filter(negocio_id=negocio_id, activo=True).exists():
        return JsonResponse(
            {
                "ok": False,
                "error": "No hay conexiones de correo activas para sincronizar.",
                "code": "no_active_mail_connections",
            },
            status=400,
        )

    lock_key = f"sync_facturas_negocio_{negocio_id}"
    if not cache.add(lock_key, "running", timeout=90):
        return JsonResponse(
            {
                "ok": False,
                "error": "Ya hay una sincronización en progreso.",
                "code": "sync_in_progress",
            },
            status=409,
        )

    try:
        resultados = sync_facturas(
            year=year_actual,
            solo_unread=True,
            negocio_id=negocio_id,
        )

        resumen = {
            "facturas_creadas": sum(r["creadas"] for r in resultados),
            "facturas_omitidas": sum(r["omitidas"] for r in resultados),
            "facturas_duplicadas": sum(r["duplicadas"] for r in resultados),
            "correos_sin_xml": sum(r["sin_xml"] for r in resultados),
            "xml_invalidos": sum(r["xml_invalido"] for r in resultados),
            "errores": sum(r["errores"] for r in resultados),
            "correos_procesados": sum(r["procesadas"] for r in resultados),
        }

        return JsonResponse(
            {
                "ok": True,
                "year": year_actual,
                "resultados": resultados,
                **resumen,
            }
        )

    except Exception as e:
        return JsonResponse(
            {
                "ok": False,
                "error": str(e),
            },
            status=500,
        )
    finally:
        cache.delete(lock_key)
