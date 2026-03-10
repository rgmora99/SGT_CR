from django.contrib import admin

from .models import Cliente


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ("nombre", "identificacion", "correo_electronico", "telefono", "estado", "actualizado_en")
    search_fields = ("nombre", "identificacion", "correo_electronico", "telefono")
    list_filter = ("estado",)
