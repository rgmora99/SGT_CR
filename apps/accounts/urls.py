from django.urls import path
from .views import login_view, logout_view, register_view, onboarding_fiscal, onboarding_negocio, perfil_view, configuracion_view

app_name = "accounts"

urlpatterns = [
    path("login/", login_view, name="login"),
    path("re/", logout_view, name="logout"),
    path("register/", register_view, name="register"),
    path("onboarding/negocio/", onboarding_negocio, name="onboarding_negocio"),
    path("onboarding/fiscal/", onboarding_fiscal, name="onboarding_fiscal"),
    path("perfil/", perfil_view, name="perfil"),
    path("configuracion/", configuracion_view, name="configuracion"),
    
]