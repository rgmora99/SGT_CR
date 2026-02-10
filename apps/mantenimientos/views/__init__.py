from .contrato_views import *
from .documento_views import *
from .seguimiento_views import *
from .prorroga_views import *
from .orden_pedido_views import *
from .garantia_views import *

__all__ = [
    "listar_contratos",
    "crear_contrato",
    "contrato_ver",
    "subir_documento",
    "seguimiento_contrato",
    "listar_prorrogas",
    "crear_prorroga",
    "listar_ordenes",
    "crear_orden",
    "listar_garantias",
    "crear_garantia",
]
