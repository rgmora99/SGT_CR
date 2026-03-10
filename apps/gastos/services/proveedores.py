from apps.gastos.models import ProveedorGasto


def registrar_o_recuperar_proveedor(negocio, nombre, defaults=None):
    nombre_limpio = (nombre or "Proveedor sin nombre").strip() or "Proveedor sin nombre"
    normalizado = nombre_limpio.lower()
    defaults = defaults or {}

    proveedor, _ = ProveedorGasto.objects.get_or_create(
        negocio=negocio,
        nombre_normalizado=normalizado,
        defaults={"nombre": nombre_limpio, **defaults},
    )
    return proveedor
