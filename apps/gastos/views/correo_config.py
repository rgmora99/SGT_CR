from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from apps.gastos.forms import ConfigCorreoFacturaForm
from apps.gastos.models import ConfigCorreoFactura
from apps.gastos.services import IMAPClient


@login_required
def config_correo_facturas(request):
    negocio_id = request.session.get("negocio_activo_id")
    if not negocio_id:
        messages.error(request, "No hay negocio activo en sesión.")
        return redirect("core:home")

    conexiones = ConfigCorreoFactura.objects.filter(negocio_id=negocio_id)

    edit_id = request.GET.get("edit")
    edit_instance = None
    if edit_id:
        edit_instance = get_object_or_404(conexiones, pk=edit_id)

    if request.method == "POST":
        action = request.POST.get("action", "save")

        if action == "delete":
            config = get_object_or_404(conexiones, pk=request.POST.get("config_id"))
            config.delete()
            messages.success(request, "Conexión eliminada correctamente.")
            return redirect("gastos:config_correo_facturas")

        target_instance = None
        config_id = request.POST.get("config_id")
        if config_id:
            target_instance = get_object_or_404(conexiones, pk=config_id)

        form = ConfigCorreoFacturaForm(request.POST, instance=target_instance)
        if form.is_valid():
            cfg = form.save(commit=False)
            cfg.negocio_id = negocio_id

            password_for_test = cfg.password
            if target_instance and not form.cleaned_data.get("password"):
                password_for_test = target_instance.password

            try:
                client = IMAPClient(cfg.imap_host, cfg.imap_port, cfg.imap_ssl)
                client.connect(cfg.username, password_for_test)
                client.select_folder(cfg.carpeta)
                client.logout()
            except Exception as e:
                messages.error(request, f"No se pudo conectar al correo: {e}")
                return render(
                    request,
                    "gastos/config_correo_facturas.html",
                    {
                        "form": form,
                        "conexiones": conexiones,
                        "edit_instance": target_instance,
                    },
                )

            cfg.save()
            messages.success(request, "Conexión guardada y validada correctamente.")
            return redirect("gastos:config_correo_facturas")

        messages.error(request, "Revisa los campos del formulario.")
    else:
        form = ConfigCorreoFacturaForm(instance=edit_instance)

    return render(
        request,
        "gastos/config_correo_facturas.html",
        {
            "form": form,
            "conexiones": conexiones,
            "edit_instance": edit_instance,
        },
    )
