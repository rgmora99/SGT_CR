from urllib import request
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.contrib.auth.models import Group, User
from django.db import transaction
from .forms import RegisterForm,ConfigFiscalForm, NegocioForm
from .models import TB_USUARIOS_APP, TB_USUARIO_NEGOCIO, TB_NEGOCIOS
from .models import TB_CONFIG_FISCAL_NEGOCIO

@require_http_methods(["GET", "POST"])
def login_view(request):
    if request.user.is_authenticated:
        return redirect("core:home")

    if request.method == "POST":
        username = (request.POST.get("username") or "").strip()
        password = (request.POST.get("password") or "").strip()

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect("core:home")

        # ⬇️ IMPORTANTE: NO redirigir, solo renderizar con error
        messages.error(request, "Usuario o contraseña incorrectos.")

    return render(request, "registration/login.html")


def logout_view(request):
    logout(request)
    return redirect("accounts:login")

@transaction.atomic
def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            nombre = form.cleaned_data["nombre"].strip()
            apellido1 = form.cleaned_data["apellido1"].strip()
            apellido2 = form.cleaned_data["apellido2"].strip()
            email = form.cleaned_data["email"].lower()
            username = form.cleaned_data["username"].strip()
            password = form.cleaned_data["password1"]

            # 1) crea auth_user
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=nombre,  # si quieres separarlo luego, lo ajustas
                last_name=f"{apellido1} {apellido2}"
            )

            # 2) asigna rol default (grupo) si existe
            # crea el grupo EMPRENDEDOR desde admin una vez
            grupo = Group.objects.filter(name="usuario").first()
            if grupo:
                user.groups.add(grupo)

            # 3) crea tu perfil extendido TB_USUARIOS_APP
            TB_USUARIOS_APP.objects.create(user=user)

            # 4) login automático
            user_auth = authenticate(
                request,
                username=username,
                password=password
            )

            if user_auth is not None:
                login(request, user_auth)

            # 5) redirige al onboarding step 1
            return redirect("accounts:onboarding_fiscal")

    else:
        form = RegisterForm()

    return render(request, "registration/register.html", {"form": form})


@login_required
def onboarding_negocio(request):
    if request.method == "POST":
        form = NegocioForm(request.POST)
        if form.is_valid():
            negocio = form.save()

            TB_USUARIO_NEGOCIO.objects.create(
                user=request.user,
                negocio=negocio,
                rol_en_negocio="usuario"
            )

            return redirect("accounts:onboarding_fiscal")

    else:
        form = NegocioForm()

    return render(
        request,
        "registration/onboarding/step_1.html",
        {"form": form}
    )

@login_required
def onboarding_fiscal(request):
    relacion = TB_USUARIO_NEGOCIO.objects.filter(user=request.user).first()

    # ⛔ si no tiene negocio, devolverlo al paso 1
    if not relacion:
        return redirect("accounts:onboarding_negocio")

    negocio = relacion.negocio

    if request.method == "POST":
        form = ConfigFiscalForm(request.POST)
        if form.is_valid():
            TB_CONFIG_FISCAL_NEGOCIO.objects.create(
                negocio=negocio,
                **form.cleaned_data
            )
            return redirect("core:home")
        
    else:
        form = ConfigFiscalForm()

    return render(
        request,
        "registration/onboarding/step_2.html",
        {"form": form, "negocio": negocio}
    )
   
from .models import TB_USUARIOS_APP, TB_NEGOCIOS

@login_required
def perfil_view(request):
    # 🔒 Garantiza que el perfil exista
    perfil, _ = TB_USUARIOS_APP.objects.get_or_create(
        user=request.user
    )

    # Rol en el negocio activo
    negocio_id = request.session.get("negocio_activo_id")
    rol = None
    negocio_activo = None

    if negocio_id:
        relacion = request.user.negocios.filter(
            negocio_id=negocio_id
        ).first()

        if relacion:
            rol = relacion
            negocio_activo = relacion.negocio

    return render(
        request,
        "accounts/perfil.html",
        {
            "perfil": perfil,
            "rol": rol,
            "negocio_activo": negocio_activo,
        }
    )

@login_required
@transaction.atomic
def configuracion_view(request):
    """
    Pantalla de configuración:
    - Edición de Negocio
    - Edición de Perfil Fiscal
    """

    # ===============================
    # 1. Obtener negocio activo
    # ===============================
    negocio_id = request.session.get("negocio_activo_id")

    if not negocio_id:
        messages.warning(request, "No hay un negocio activo seleccionado.")
        return redirect("core:home")

    # Validar que el negocio pertenezca al usuario
    rol = TB_USUARIO_NEGOCIO.objects.filter(
        user=request.user,
        negocio_id=negocio_id
    ).first()

    if not rol:
        messages.error(request, "No tienes permisos sobre este negocio.")
        return redirect("core:home")

    negocio = get_object_or_404(TB_NEGOCIOS, id_negocio=negocio_id)

    # Config fiscal (1–1)
    config_fiscal, _ = TB_CONFIG_FISCAL_NEGOCIO.objects.get_or_create(
        negocio=negocio
    )

    # ===============================
    # 2. POST – Guardar cambios
    # ===============================
    if request.method == "POST":
        form_type = request.POST.get("form_type")

        # -------------------------------
        # A. ACTUALIZAR NEGOCIO
        # -------------------------------
        if form_type == "negocio":
            nombre = request.POST.get("nombre_comercial", "").strip()
            provincia = request.POST.get("provincia", "").strip()
            moneda = request.POST.get("moneda_base")

            if not nombre:
                messages.error(request, "El nombre comercial es obligatorio.")
            elif moneda not in ("CRC", "USD"):
                messages.error(request, "Moneda base inválida.")
            else:
                negocio.nombre_comercial = nombre
                negocio.provincia = provincia
                negocio.moneda_base = moneda
                negocio.save()

                messages.success(request, "Información del negocio actualizada.")
                return redirect("accounts:configuracion")

        # -------------------------------
        # B. ACTUALIZAR PERFIL FISCAL
        # -------------------------------
        elif form_type == "fiscal":
            tipo_ident = request.POST.get("tipo_identificacion")
            identificacion = request.POST.get("identificacion", "").strip()
            regimen_iva = request.POST.get("regimen_iva")
            aplica_iva = request.POST.get("aplica_iva") == "true"
            porc_iva = request.POST.get("porc_iva")
            periodo_iva = request.POST.get("periodo_iva")
            declara_renta = request.POST.get("declara_renta") == "true"

            # Validaciones
            errores = []

            if not tipo_ident:
                errores.append("Debe seleccionar el tipo de identificación.")

            if not identificacion:
                errores.append("La identificación es obligatoria.")

            if aplica_iva:
                if not porc_iva:
                    errores.append("Debe indicar el porcentaje de IVA.")
                else:
                    try:
                        porc_iva = float(porc_iva)
                        if porc_iva <= 0 or porc_iva > 100:
                            errores.append("El % de IVA debe ser válido.")
                    except ValueError:
                        errores.append("El % de IVA debe ser numérico.")
            else:
                porc_iva = None
                periodo_iva = None

            if errores:
                for e in errores:
                    messages.error(request, e)
            else:
                config_fiscal.tipo_identificacion = tipo_ident
                config_fiscal.identificacion = identificacion
                config_fiscal.regimen_iva = regimen_iva
                config_fiscal.aplica_iva = aplica_iva
                config_fiscal.porc_iva = porc_iva
                config_fiscal.periodo_iva = periodo_iva
                config_fiscal.declara_renta = declara_renta
                config_fiscal.save()

                messages.success(request, "Perfil fiscal actualizado correctamente.")
                return redirect("accounts:configuracion")

    provincias = TB_NEGOCIOS._meta.get_field("provincia").choices
    # ===============================
    # 3. GET – Renderizar vista
    # ===============================
    return render(
        request,
        "accounts/configuracion.html",
        {
            "negocio": negocio,
            "config_fiscal": config_fiscal,
            "rol": rol,
            "provincias": provincias,
        }
    )