from apps.gastos.models import ProveedorGasto
from apps.gastos.services.xml_factura_parser import parse_factura_xml


def registrar_o_recuperar_proveedor(negocio, nombre, defaults=None):
    nombre_limpio = (nombre or "Proveedor sin nombre").strip() or "Proveedor sin nombre"
    normalizado = nombre_limpio.lower()
    defaults = defaults or {}

    proveedor, created = ProveedorGasto.objects.get_or_create(
        negocio=negocio,
        nombre_normalizado=normalizado,
        defaults={"nombre": nombre_limpio, **defaults},
    )

    if not created:
        campos_actualizables = ["identificacion", "email", "telefono"]
        cambios = []
        for campo in campos_actualizables:
            valor_actual = getattr(proveedor, campo)
            valor_nuevo = (defaults.get(campo) or "").strip() if isinstance(defaults.get(campo), str) else defaults.get(campo)
            if not valor_actual and valor_nuevo:
                setattr(proveedor, campo, valor_nuevo)
                cambios.append(campo)

        if cambios:
            proveedor.save(update_fields=cambios)

    return proveedor


def defaults_proveedor_desde_factura(factura):
    defaults = {
        "identificacion": factura.proveedor_identificacion or None,
        "email": factura.proveedor_email or factura.email_from or None,
        "telefono": factura.proveedor_telefono or None,
    }

    if factura.xml_file and not all(defaults.values()):
        try:
            factura.xml_file.open("rb")
            xml_bytes = factura.xml_file.read()
            factura.xml_file.close()
            parsed = parse_factura_xml(xml_bytes)

            defaults["identificacion"] = defaults["identificacion"] or parsed.get("proveedor_cedula") or None
            defaults["email"] = defaults["email"] or parsed.get("proveedor_email") or None
            defaults["telefono"] = defaults["telefono"] or parsed.get("proveedor_telefono") or None

            if not factura.proveedor_identificacion and defaults["identificacion"]:
                factura.proveedor_identificacion = defaults["identificacion"]
            if not factura.proveedor_email and defaults["email"]:
                factura.proveedor_email = defaults["email"]
            if not factura.proveedor_telefono and defaults["telefono"]:
                factura.proveedor_telefono = defaults["telefono"]
            factura.save(update_fields=["proveedor_identificacion", "proveedor_email", "proveedor_telefono"])
        except Exception:
            pass

    return defaults
