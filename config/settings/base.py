from pathlib import Path
import os
from dotenv import load_dotenv
# ==========================
# BASE DIR
# ==========================
BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / ".env")
# ==========================
# SECURITY
# ==========================
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'django-insecure-change-me')
DEBUG = os.getenv('DJANGO_DEBUG', 'true').lower() in ('1', 'true', 'yes')
ALLOWED_HOSTS = []

# ==========================
# APPLICATIONS
# ==========================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Apps del proyecto
    #'apps.contratos.apps.ContratosConfig',
    "apps.accounts",
    "apps.alertas",
    "apps.ventas",
    "apps.gastos",
    #"apps.catalogos",
    #"apps.proveedores",
]

AUTHENTICATION_BACKENDS = [
    "apps.accounts.backends.LDAPBackend",
    "django.contrib.auth.backends.ModelBackend",
]

# ==========================
# MIDDLEWARE
# ==========================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
     "apps.accounts.middleware.OnboardingMiddleware",
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    
]

# ==========================
# URL / WSGI
# ==========================
ROOT_URLCONF = 'config.urls'
WSGI_APPLICATION = 'config.wsgi.application'

# ==========================
# TEMPLATES
# ==========================
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# ==========================
# DATABASE
# ==========================

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "DE_CONT",
        "USER": "usr_cnt",
        "PASSWORD": "usr_cnt",
        "HOST": "localhost",   # IP del servidor PostgreSQL
        "PORT": "5432",
        "OPTIONS": {
            "options": "-c search_path=cnt"
        },
        "CONN_MAX_AGE": 60,    # recomendado producción
    }
}
# ==========================
# AUTH
# ==========================
LOGIN_URL = "accounts:login"
LOGIN_REDIRECT_URL = "home"
LOGOUT_REDIRECT_URL = "accounts:login"

# ==========================
# I18N
# ==========================
LANGUAGE_CODE = 'es-cr'
TIME_ZONE = 'America/Costa_Rica'
USE_I18N = True
USE_TZ = True

# ==========================
# STATIC FILES
# ==========================
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

# ==========================
# MEDIA FILES
# ==========================
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
