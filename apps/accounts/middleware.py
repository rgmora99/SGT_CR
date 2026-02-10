from django.shortcuts import redirect
from django.urls import reverse
from apps.accounts.models import (
    TB_USUARIO_NEGOCIO,
    TB_CONFIG_FISCAL_NEGOCIO
)

class OnboardingMiddleware:
    """
    - Obliga a completar onboarding
    - Define negocio activo en sesión
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Si no está logueado, no hacemos nada
        if not request.user.is_authenticated:
            return self.get_response(request)

        path = request.path

        # Rutas que NO deben bloquearse
        rutas_permitidas = [
            reverse("accounts:onboarding_negocio"),
            reverse("accounts:onboarding_fiscal"),
            reverse("accounts:logout"),
        ]

        # Permitir estáticos y admin
        if (
            path.startswith("/static/")
            or path.startswith("/admin/")
        ):
            return self.get_response(request)

        # ==========================
        # 1. Validar negocio del usuario
        # ==========================
        relaciones = TB_USUARIO_NEGOCIO.objects.filter(user=request.user)

        if not relaciones.exists():
            # No tiene negocio → Step 1
            if path not in rutas_permitidas:
                return redirect("accounts:onboarding_negocio")
            return self.get_response(request)

        # ==========================
        # 2. Definir negocio activo
        # ==========================
        negocio_activo_id = request.session.get("negocio_activo_id")

        if not negocio_activo_id:
            # Si solo tiene uno, lo ponemos automático
            negocio_activo_id = relaciones.first().negocio_id
            request.session["negocio_activo_id"] = negocio_activo_id

        # ==========================
        # 3. Validar perfil fiscal completo
        # ==========================
        try:
            config = TB_CONFIG_FISCAL_NEGOCIO.objects.get(
                negocio_id=negocio_activo_id
            )
        except TB_CONFIG_FISCAL_NEGOCIO.DoesNotExist:
            if path not in rutas_permitidas:
                return redirect("accounts:onboarding_fiscal")
            return self.get_response(request)

        # Validación mínima de campos obligatorios
        if not config.periodo_iva:
            if path not in rutas_permitidas:
                return redirect("accounts:onboarding_fiscal")

        return self.get_response(request)