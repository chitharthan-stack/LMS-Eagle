from pathlib import Path
import os
from datetime import timedelta
import dj_database_url
from dotenv import load_dotenv

# Base dir
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env (local dev)
load_dotenv(BASE_DIR / ".env")

# -----------------------
# SECURITY / basic envs
# -----------------------
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", os.getenv("DJANGO_SECRET_KEY", "dev-secret-key"))

# DEBUG allowed values: "true","1","yes" are truthy
DEBUG = os.getenv("DEBUG", "true").lower() in ("1", "true", "yes")

# ALLOWED_HOSTS: comma separated list in env, fallback to localhost for dev
ALLOWED_HOSTS = [h.strip() for h in os.getenv("ALLOWED_HOSTS", "127.0.0.1,localhost").split(",") if h.strip()]

# If you deploy behind a proxy (Vercel), set this header to honor scheme
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Redirect HTTP to HTTPS in production (toggle via env)
SECURE_SSL_REDIRECT = os.getenv("SECURE_SSL_REDIRECT", "false").lower() in ("1", "true", "yes")

# Cookie security in production
SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "false").lower() in ("1", "true", "yes")
CSRF_COOKIE_SECURE = os.getenv("CSRF_COOKIE_SECURE", "false").lower() in ("1", "true", "yes")

# Set CSRF trusted origins as comma separated list if needed (e.g. your domain)
csrf_origins = os.getenv("CSRF_TRUSTED_ORIGINS", "")
CSRF_TRUSTED_ORIGINS = [u.strip() for u in csrf_origins.split(",") if u.strip()] if csrf_origins else []

# -----------------------
# INSTALLED_APPS
# -----------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Postgres specific fields
    "django.contrib.postgres",

    # Third-party
    "rest_framework",
    "django_filters",
    "corsheaders",
    "rest_framework_simplejwt.token_blacklist",
    "drf_spectacular",
    "drf_spectacular_sidecar",
    "whitenoise.runserver_nostatic",  # helps WhiteNoise on dev server

    # Local apps
    "LMS_users",
    "api",

    # Dev tools (optional)
    "django_extensions",
]

# -----------------------
# MIDDLEWARE
# -----------------------
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # serve static files
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# -----------------------
# URLS & WSGI/ASGI
# -----------------------
ROOT_URLCONF = "lms_backend.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "lms_backend.wsgi.application"
ASGI_APPLICATION = "lms_backend.asgi.application"

# -----------------------
# DATABASE
# -----------------------
# Uses dj_database_url to parse DATABASE_URL env var (Neon / Postgres)
DATABASES = {
    "default": dj_database_url.config(
        env="DATABASE_URL",
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=int(os.getenv("DB_CONN_MAX_AGE", "600")),
    )
}

# -----------------------
# AUTH
# -----------------------
AUTH_USER_MODEL = "LMS_users.User"

# -----------------------
# REST FRAMEWORK + JWT
# -----------------------
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.AllowAny",
    ),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
    # pagination default (you can override per-view)
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": int(os.getenv("PAGE_SIZE", "25")),
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=int(os.getenv("JWT_ACCESS_MINUTES", "60"))),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=int(os.getenv("JWT_REFRESH_DAYS", "7"))),
    "AUTH_HEADER_TYPES": ("Bearer",),
}

# -----------------------
# STATIC & MEDIA (WhiteNoise)
# -----------------------
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]

# Use WhiteNoise compressed storage in production
STATICFILES_STORAGE = os.getenv(
    "STATICFILES_STORAGE",
    "whitenoise.storage.CompressedManifestStaticFilesStorage"
)

# Media (user uploaded files) — container FS is ephemeral on Vercel; use S3 for permanent storage
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# If you plan to use S3 for media, set DEFAULT_FILE_STORAGE to storages backend in env or here:
# DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"

# -----------------------
# CORS
# -----------------------
CORS_ALLOW_ALL_ORIGINS = os.getenv("CORS_ALLOW_ALL_ORIGINS", "true").lower() in ("1", "true", "yes")
CORS_ALLOWED_ORIGINS = [u.strip() for u in os.getenv("CORS_ALLOWED_ORIGINS", "").split(",") if u.strip()]
CORS_ALLOW_CREDENTIALS = os.getenv("CORS_ALLOW_CREDENTIALS", "true").lower() in ("1", "true", "yes")

# -----------------------
# Internationalization
# -----------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = os.getenv("TIME_ZONE", "Asia/Kolkata")
USE_I18N = True
USE_TZ = True

# -----------------------
# DEFAULTS
# -----------------------
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# -----------------------
# API Docs (drf-spectacular)
# -----------------------
SPECTACULAR_SETTINGS = {
    "TITLE": "LMS API",
    "VERSION": os.getenv("API_VERSION", "0.0.0"),
    "SERVE_INCLUDE_SCHEMA": False,
    "COMPONENT_SPLIT_REQUEST": True,
    "SECURITY": [{"jwtAuth": []}],
    "SWAGGER_UI_SETTINGS": {"persistAuthorization": True},
}

# -----------------------
# Email
# -----------------------
EMAIL_BACKEND = os.getenv("EMAIL_BACKEND", "django.core.mail.backends.smtp.EmailBackend")
EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "465"))
EMAIL_USE_SSL = os.getenv("EMAIL_USE_SSL", "True").lower() in ("1", "true", "yes")
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", EMAIL_HOST_USER)
EMAIL_TIME_ZONE = os.getenv("EMAIL_TIME_ZONE", "UTC")

# -----------------------
# Logging (simple)
# -----------------------
LOG_LEVEL = os.getenv("DJANGO_LOG_LEVEL", "INFO")

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {"format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"},
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "standard"},
    },
    "loggers": {
        "": {"handlers": ["console"], "level": LOG_LEVEL},
        "django": {"handlers": ["console"], "level": LOG_LEVEL, "propagate": False},
    },
}

# -----------------------
# Optional: Security headers
# -----------------------
# Recommended in production; enable via env to avoid interfering with local dev
SECURE_HSTS_SECONDS = int(os.getenv("SECURE_HSTS_SECONDS", "0"))  # e.g. 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = os.getenv("SECURE_HSTS_INCLUDE_SUBDOMAINS", "false").lower() in ("1", "true", "yes")
SECURE_HSTS_PRELOAD = os.getenv("SECURE_HSTS_PRELOAD", "false").lower() in ("1", "true", "yes")
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = "DENY"

# -----------------------
# Helpful dev toggles
# -----------------------
# Whether to run collectstatic/migrate on container start is controlled in your entrypoint.sh
RUN_MIGRATIONS_ON_START = os.getenv("RUN_MIGRATIONS_ON_START", "false").lower() in ("1", "true", "yes")

# -----------------------
# End of file
# -----------------------
