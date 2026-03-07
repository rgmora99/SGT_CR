from django.db.models import Q
from django.shortcuts import redirect
from django.utils import timezone

from apps.gastos.models import ConfigCorreoFactura, FacturaGasto
from apps.gastos.services import (
    IMAPClient,
    crear_factura_desde_correo,
    existe_por_message_id,
    extract_xml_pdf,
    parse_email,
    parse_factura_xml,
)
from apps.gastos.services.gastos_fijos import aplicar_gasto_fijo_a_factura


def _existe_factura_por_contenido(negocio_id, factura_data):
    """Fallback de deduplicación cuando no hay Message-ID confiable."""
    return FacturaGasto.objects.filter(
        negocio_id=negocio_id,
        numero_factura=factura_data.get("numero_factura") or "",
        fecha_emision=factura_data.get("fecha_emision"),
        total=factura_data.get("total") or 0,
    ).filter(
        Q(proveedor=factura_data.get("proveedor") or "")
        | Q(email_from__icontains=factura_data.get("proveedor") or "")
    ).exists()


def sync_facturas(*, year=None, solo_unread=True, negocio_id=None):
    """
    Sincroniza facturas desde correo.

    Args:
        year (int | None): año a sincronizar
        solo_unread (bool): solo correos no leídos
        negocio_id (int | None): si se envía, limita la sincronización a un negocio

    Returns:
        list[dict]: resultados por negocio/conexión
    """

    resultados = []

    configs = ConfigCorreoFactura.objects.filter(activo=True)
    if negocio_id:
        configs = configs.filter(negocio_id=negocio_id)

    for cfg in configs:
        stats = {
            "creadas": 0,
            "duplicadas": 0,
            "sin_xml": 0,
            "xml_invalido": 0,
            "errores": 0,
            "procesadas": 0,
        }

        client = IMAPClient(cfg.imap_host, cfg.imap_port, cfg.imap_ssl)

        try:
            client.connect(cfg.username, cfg.password)
            client.select_folder(cfg.carpeta)

            if year:
                ids = client.search_by_year(
                    year=year,
                    subject=None,
                    unseen_only=solo_unread,
                )
            else:
                ids = client.search_unseen()

            for msg_id in ids:
                stats["procesadas"] += 1

                try:
                    raw = client.fetch_rfc822(msg_id)
                    msg, meta = parse_email(raw)
                except Exception:
                    stats["errores"] += 1
                    continue

                message_id = (meta.get("message_id") or "").strip()

                if existe_por_message_id(cfg.negocio_id, message_id):
                    stats["duplicadas"] += 1
                    continue

                xml_bytes, pdf_bytes, xml_name, pdf_name = extract_xml_pdf(msg)
                if not xml_bytes:
                    stats["sin_xml"] += 1
                    continue

                try:
                    factura_data = parse_factura_xml(xml_bytes)
                except Exception:
                    stats["xml_invalido"] += 1
                    continue

                if _existe_factura_por_contenido(cfg.negocio_id, factura_data):
                    stats["duplicadas"] += 1
                    continue

                try:
                    crear_factura_desde_correo(
                        negocio=cfg.negocio,
                        usuario=None,
                        meta=meta,
                        factura_data=factura_data,
                        xml_bytes=xml_bytes,
                        xml_name=xml_name or "factura.xml",
                        pdf_bytes=pdf_bytes,
                        pdf_name=pdf_name or "factura.pdf",
                    )
                    client.mark_seen(msg_id)
                    stats["creadas"] += 1
                except Exception:
                    stats["errores"] += 1
                    continue

            cfg.ultima_sync = timezone.now()
            cfg.save(update_fields=["ultima_sync"])

        finally:
            client.logout()

        resultados.append(
            {
                "negocio": cfg.negocio_id,
                "conexion": cfg.id,
                **stats,
                "omitidas": stats["duplicadas"] + stats["sin_xml"] + stats["xml_invalido"],
            }
        )

    return resultados


def aplicar_reglas_gastos_fijos(request):
    """Aplica reglas de gastos fijos sobre facturas pendientes del negocio activo."""
    negocio_id = request.session.get("negocio_activo_id")
    if not negocio_id:
        return redirect("gastos:bandeja_facturas")

    facturas = FacturaGasto.objects.filter(
        negocio_id=negocio_id,
        estado__in=["pendiente", "en_registro"],
    ).select_related("categoria")

    for factura in facturas:
        aplicar_gasto_fijo_a_factura(factura)

    return redirect("gastos:bandeja_facturas")
