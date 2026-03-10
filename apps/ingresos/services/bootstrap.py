from apps.ingresos.models import CategoriaIngreso


CATEGORIAS_POR_DEFECTO = [
    "Ventas de productos",
    "Servicios profesionales",
    "Alquileres",
    "Comisiones",
    "Otros ingresos",
]


def asegurar_categorias_base(negocio_id):
    if not negocio_id:
        return
    existentes = set(
        CategoriaIngreso.objects.filter(negocio_id=negocio_id).values_list("nombre", flat=True)
    )
    nuevas = [
        CategoriaIngreso(negocio_id=negocio_id, nombre=nombre)
        for nombre in CATEGORIAS_POR_DEFECTO
        if nombre not in existentes
    ]
    if nuevas:
        CategoriaIngreso.objects.bulk_create(nuevas)


from apps.ingresos.models import ProductoIngreso

PRODUCTOS_BASE = [
    ("SERV-001", "Servicio general", "0.00"),
    ("PROD-001", "Producto estándar", "0.00"),
]


def asegurar_productos_base(negocio_id):
    if not negocio_id:
        return
    existentes = set(ProductoIngreso.objects.filter(negocio_id=negocio_id).values_list("codigo", flat=True))
    nuevos = [
        ProductoIngreso(negocio_id=negocio_id, codigo=c, nombre=n, precio_base=p)
        for c, n, p in PRODUCTOS_BASE
        if c not in existentes
    ]
    if nuevos:
        ProductoIngreso.objects.bulk_create(nuevos)
