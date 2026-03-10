from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.http import JsonResponse
from django.utils.timezone import now
from django.views.decorators.http import require_POST

from apps.gastos.models import ConfigCorreoFactura, FacturaGasto
from apps.gastos.services.sync_facturas import sync_facturas
from apps.gastos.services.xml_factura_parser import parse_factura_xml


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


@login_required
@require_POST
def recargar_metadata_facturas_ajax(request):
    """
    Recalcula moneda/tipo/alerta en facturas existentes a partir del XML guardado.
    Útil para normalizar datos históricos tras mejoras de parser.
    """

    negocio_id = request.session.get("negocio_activo_id")
    if not negocio_id:
        return JsonResponse(
            {"ok": False, "error": "No hay negocio activo en sesión."},
            status=400,
        )

    lock_key = f"recalculo_facturas_negocio_{negocio_id}"
    if not cache.add(lock_key, "running", timeout=180):
        return JsonResponse(
            {
                "ok": False,
                "error": "Ya hay un recálculo en progreso.",
                "code": "reload_in_progress",
            },
            status=409,
        )

    actualizadas = 0
    sin_xml = 0
    errores = 0

    try:
        facturas = FacturaGasto.objects.filter(
            negocio_id=negocio_id,
            estado__in=["pendiente", "en_registro", "registrada"],
        ).only(
            "id",
            "xml_file",
            "moneda",
            "tipo_documento_xml",
            "alerta_ingesta",
            "proveedor_identificacion",
            "proveedor_email",
            "proveedor_telefono",
        )

        for factura in facturas:
            if not factura.xml_file:
                sin_xml += 1
                continue

            try:
                factura.xml_file.open("rb")
                xml_bytes = factura.xml_file.read()
                factura.xml_file.close()

                data = parse_factura_xml(xml_bytes)
                factura.moneda = data.get("moneda", factura.moneda or "CRC")
                factura.tipo_documento_xml = data.get("tipo_documento_xml", factura.tipo_documento_xml)
                factura.alerta_ingesta = data.get("alerta_ingesta")
                factura.proveedor_identificacion = data.get("proveedor_cedula") or factura.proveedor_identificacion
                factura.proveedor_email = data.get("proveedor_email") or factura.proveedor_email
                factura.proveedor_telefono = data.get("proveedor_telefono") or factura.proveedor_telefono
                factura.save(
                    update_fields=[
                        "moneda",
                        "tipo_documento_xml",
                        "alerta_ingesta",
                        "proveedor_identificacion",
                        "proveedor_email",
                        "proveedor_telefono",
                    ]
                )
                actualizadas += 1
            except Exception:
                errores += 1

        return JsonResponse(
            {
                "ok": True,
                "actualizadas": actualizadas,
                "sin_xml": sin_xml,
                "errores": errores,
            }
        )
    finally:
        cache.delete(lock_key)
