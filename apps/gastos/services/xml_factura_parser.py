import xml.etree.ElementTree as ET
from datetime import date, datetime
from decimal import Decimal, InvalidOperation


def _tag_local_name(tag: str) -> str:
    return tag.split("}")[-1] if "}" in tag else tag


def _find_text(root, *candidates):
    candidate_set = {c.lower() for c in candidates}
    for node in root.iter():
        if _tag_local_name(node.tag).lower() in candidate_set:
            text = (node.text or "").strip()
            if text:
                return text
    return ""


def _find_node(root, candidate):
    target = candidate.lower()
    for node in root.iter():
        if _tag_local_name(node.tag).lower() == target:
            return node
    return None


def _find_text_in_node(node, *candidates):
    if node is None:
        return ""
    return _find_text(node, *candidates)


def _to_decimal(value, default="0"):
    try:
        return Decimal(str(value or default).strip())
    except (InvalidOperation, ValueError, TypeError):
        return Decimal(default)


def _to_date(value):
    if not value:
        return date.today(), "No se encontró fecha en el XML; se usó fecha actual."

    value = value.strip()
    try:
        return datetime.fromisoformat(value[:19]).date(), None
    except Exception:
        return date.today(), "Fecha del XML inválida; se usó fecha actual."


def parse_factura_xml(xml_bytes):
    root = ET.fromstring(xml_bytes)
    root_name = _tag_local_name(root.tag).lower()
    emisor_node = _find_node(root, "Emisor")

    numero = _find_text(root, "NumeroConsecutivo", "NumeroConsecutivoReceptor", "NumeroDocumento") or "SIN_NUM"
    proveedor = (
        _find_text_in_node(emisor_node, "Nombre", "NombreComercial")
        or _find_text(root, "NombreEmisor", "Nombre")
        or "Proveedor desconocido"
    )

    proveedor_cedula = (
        _find_text_in_node(emisor_node, "Numero")
        or _find_text(root, "NumeroCedulaEmisor", "NumeroEmisor")
    )
    proveedor_email = (
        _find_text_in_node(emisor_node, "CorreoElectronico", "Correo")
        or _find_text(root, "CorreoEmisor")
    )
    proveedor_telefono = (
        _find_text_in_node(emisor_node, "NumTelefono", "Telefono")
        or _find_text(root, "TelefonoEmisor")
    )

    fecha_emision, alerta_fecha = _to_date(_find_text(root, "FechaEmision", "FechaEmisionDoc"))

    subtotal = _to_decimal(_find_text(root, "TotalVentaNeta", "TotalVenta"))
    iva = _to_decimal(_find_text(root, "TotalImpuesto", "TotalImpuestoAsumidoEmisor"))
    total = _to_decimal(_find_text(root, "TotalComprobante", "TotalFactura", "MontoTotalImpuestoAcreditar"))

    moneda = (
        _find_text(root, "CodigoMoneda", "Moneda", "CodigoTipoMoneda")
        or "CRC"
    ).upper()

    alerta = alerta_fecha
    tipo_documento = "factura_electronica"

    if "mensajehacienda" in root_name:
        tipo_documento = "mensaje_hacienda"
        if not alerta:
            alerta = "XML tipo MensajeHacienda: revisar manualmente antes de registrar el gasto."

        # En MensajeHacienda muchas veces no vienen montos completos.
        if total == Decimal("0"):
            alerta = (alerta + " " if alerta else "") + "No se detectó total en MensajeHacienda."

    elif "notacredito" in root_name:
        tipo_documento = "nota_credito"
    elif "notadebito" in root_name:
        tipo_documento = "nota_debito"
    elif "tiqueteelectronico" in root_name:
        tipo_documento = "tiquete_electronico"

    if moneda not in {"CRC", "USD"}:
        alerta_moneda = f"Moneda detectada no estándar ({moneda}); validar tipo de cambio/manual."
        alerta = f"{alerta} {alerta_moneda}".strip() if alerta else alerta_moneda

    return {
        "numero_factura": numero,
        "fecha_emision": fecha_emision,
        "subtotal": subtotal,
        "iva": iva,
        "total": total,
        "proveedor": proveedor,
        "proveedor_cedula": proveedor_cedula,
        "proveedor_email": proveedor_email,
        "proveedor_telefono": proveedor_telefono,
        "moneda": moneda,
        "tipo_documento_xml": tipo_documento,
        "alerta_ingesta": alerta,
    }
