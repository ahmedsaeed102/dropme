import os
import base64
import environ
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from django.utils.translation import gettext_lazy as _
from datetime import timedelta
from pathlib import Path
from firebase_admin import initialize_app, credentials
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent
env = environ.Env()
env.read_env(BASE_DIR / ".env")

# Core Settings
SECRET_KEY = env("SECRET_KEY")
DEBUG = True
ALLOWED_HOSTS = ["*"]
CORS_ALLOW_ALL_ORIGINS = True
CSRF_TRUSTED_ORIGINS = ["https://*.railway.app", "https://127.0.0.1"]
SITE_ID = env.int("SITE_ID")

# Sentry
sentry_sdk.init(
    dsn=env("sentry"),
    integrations=[DjangoIntegration()],
    traces_sample_rate=1.0,
    send_default_pii=True,
)

# Installed Apps
INSTALLED_APPS = [
    "daphne",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.gis",
    # Third-party
    "rest_framework",
    "rest_framework.authtoken",
    "rest_framework_api_key",
    "channels",
    "fcm_django",
    "rest_framework_simplejwt.token_blacklist",
    "drf_spectacular",
    "drf_spectacular_sidecar",
    "corsheaders",
    "storages",
    "kronos",
    "core",
    'django_filters',
    # Internal
    "users_api",
    "community_api",
    "machine_api",
    "competition_api",
    "notification",
    "marketplace",
]

# Firebase Setup
private_key = base64.b64decode(str.encode(env("private_key"))).decode("utf-8")
cert = {
    "type": env("type"),
    "project_id": env("project_id"),
    "private_key_id": env("private_key_id"),
    "private_key": private_key.replace(r"\n", "\n"),
    "client_email": env("client_email"),
    "client_id": env("client_id"),
    "auth_uri": env("auth_uri"),
    "token_uri": env("token_uri"),
    "auth_provider_x509_cert_url": env("auth_provider_x509_cert_url"),
    "client_x509_cert_url": env("client_x509_cert_url"),
}
FIREBASE_APP = initialize_app(credentials.Certificate(cert))

FCM_DJANGO_SETTINGS = {
    "DEFAULT_FIREBASE_APP": FIREBASE_APP,
    "APP_VERBOSE_NAME": "notification",
    "ONE_DEVICE_PER_USER": False,
    "DELETE_INACTIVE_DEVICES": False,
    "UPDATE_ON_DUPLICATE_REG_ID": True,
}

# Auth
AUTH_USER_MODEL = "users_api.UserModel"
AUTHENTICATION_BACKENDS = ["core.backends.AuthBackend"]

# JWT
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=10),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "TOKEN_OBTAIN_SERIALIZER": "users_api.serializers.MyTokenObtainPairSerializer",
    "TOKEN_REFRESH_SERIALIZER": "rest_framework_simplejwt.serializers.TokenRefreshSerializer",
    "TOKEN_VERIFY_SERIALIZER": "rest_framework_simplejwt.serializers.TokenVerifySerializer",
    "TOKEN_BLACKLIST_SERIALIZER": "rest_framework_simplejwt.serializers.TokenBlacklistSerializer",
    "USER_AUTHENTICATION_RULE": "core.backends.simple_jwt_authentication_rule",
}

# DRF
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.BasicAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
    ]
}

# Swagger
SPECTACULAR_SETTINGS = {
    "TITLE": "Dropme Project api",
    "VERSION": "1.0.0",
    "SWAGGER_UI_DIST": "SIDECAR",
    "SWAGGER_UI_FAVICON_HREF": "SIDECAR",
}

# Channels
ASGI_APPLICATION = "core.asgi.application"
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    },
}

# Cache
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.db.DatabaseCache",
        "LOCATION": "cache_table",
    }
}

# Middleware
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "core.urls"

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

WSGI_APPLICATION = "core.wsgi.application"


DATABASES = {
    "default": dj_database_url.parse(env("DATABASE_URL"), conn_max_age=600, ssl_require=False),
}
DATABASES["default"]["ENGINE"] = "django.contrib.gis.db.backends.postgis"


# Email
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.zoho.com"
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False
EMAIL_PORT = 587
EMAIL_HOST_USER = env("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD")

# Storage / Static / Media
DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
AWS_S3_REGION_NAME = env("AWS_S3_REGION_NAME")
AWS_S3_ENDPOINT_URL = f"https://s3.{AWS_S3_REGION_NAME}.backblazeb2.com"
AWS_ACCESS_KEY_ID = env("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = env("AWS_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = env("AWS_STORAGE_BUCKET_NAME")

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# File Upload Limits
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024

# GDAL (for Windows local dev if needed)
if os.name == "nt":
    import platform

    OSGEO4W = r"C:\OSGeo4W"
    os.environ["OSGEO4W_ROOT"] = OSGEO4W
    os.environ["GDAL_DATA"] = OSGEO4W + r"\share\gdal"
    os.environ["PROJ_LIB"] = OSGEO4W + r"\share\proj"
    os.environ["PATH"] = OSGEO4W + r"\bin;" + os.environ["PATH"]

# This tells Django/GeoDjango where the GDAL bindings live
GDAL_LIBRARY_PATH = r"C:\OSGeo4W\bin\gdal310.dll"


# Password Validators
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Languages
LANGUAGE_CODE = "en"
LANGUAGES = [
    ("en", _("English")),
    ("ar", _("Arabic")),
]
LOCALE_PATHS = [BASE_DIR / "locale/"]
USE_I18N = True
USE_L10N = True
USE_TZ = True
TIME_ZONE = "UTC"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
MAX_OTP_TRY = 3
MIN_PASSWORD_LENGTH = 8