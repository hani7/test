import os
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "dev-secret")
DEBUG = os.getenv("DEBUG", "1") == "1"
ALLOWED_HOSTS = ["localhost", "127.0.0.1", ".onrender.com","https://test-uvee.onrender.com"]  # le point autorise tous les sous-domaines
CSRF_TRUSTED_ORIGINS = ["https://test-uvee.onrender.com"]


INSTALLED_APPS = [
    "django.contrib.admin","django.contrib.auth","django.contrib.contenttypes",
    "django.contrib.sessions","django.contrib.messages","django.contrib.staticfiles",
    "rest_framework","corsheaders",
    "fleur",  # <- ton app
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",


]

ROOT_URLCONF = "fleuriste.urls"

TEMPLATES = [{
    "BACKEND": "django.template.backends.django.DjangoTemplates",
    "DIRS": [BASE_DIR / "templates"],   # ← active le dossier /templates au niveau projet
    "APP_DIRS": True,                   # ← active templates/ à l’intérieur des apps
    "OPTIONS": {"context_processors":[
        "django.template.context_processors.debug",
        "django.template.context_processors.request",
        "django.contrib.auth.context_processors.auth",
        "django.contrib.messages.context_processors.messages",

    ]},
}]

WSGI_APPLICATION = "fleuriste.wsgi.application"
ASGI_APPLICATION = "fleuriste.asgi.application"

# DB: SQLite pour démarrer
DATABASES = {}
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    try:
        import dj_database_url
        DATABASES["default"] = dj_database_url.parse(
            DATABASE_URL,
            conn_max_age=600,
            ssl_require=os.getenv("RENDER","0")=="1"
        )
    except Exception as e:
        # fallback SQLite si le module n'est pas dispo
        print("Warning: dj_database_url indisponible, fallback SQLite:", e)
        DATABASES["default"] = {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
else:
    # pas de DATABASE_URL => SQLite local
    DATABASES["default"] = {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }

LANGUAGE_CODE = "fr-fr"
TIME_ZONE = os.getenv("TIME_ZONE","Africa/Algiers")
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "static"
CORS_ALLOW_ALL_ORIGINS = True

REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.AllowAny"],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.BasicAuthentication",
    ],
}

# Adresse de l’agent matériel
AGENT_BASE_URL = os.getenv("AGENT_BASE_URL", "http://localhost:9000")

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


