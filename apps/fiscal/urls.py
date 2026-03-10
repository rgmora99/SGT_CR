from django.urls import path

from apps.fiscal.views import dashboard_fiscal, exportar_borrador_csv

app_name = "fiscal"

urlpatterns = [
    path("", dashboard_fiscal, name="dashboard"),
    path("exportar-csv/", exportar_borrador_csv, name="exportar_csv"),
]
