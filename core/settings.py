import os
import base64
import environ
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from django.utils.translation import gettext_lazy as _
from datetime import timedelta
from pathlib import Path
from firebase_admin import initialize_app
from firebase_admin import credentials


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env()
env.read_env(BASE_DIR / ".env")

MAX_OTP_TRY = 3
AUTH_USER_MODEL = "users_api.UserModel"
MIN_PASSWORD_LENGTH = 8

SECRET_KEY = env("SECRET_KEY")
DEBUG = env.bool("DEBUG")

CSRF_TRUSTED_ORIGINS = ["https://*.railway.app", "https://127.0.0.1"]
ALLOWED_HOSTS = ["*"]
CORS_ALLOW_ALL_ORIGINS = True

# Sentry for error reporting
sentry_sdk.init(
    dsn=env("sentry"),
    integrations=[
        DjangoIntegration(),
    ],
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    # We recommend adjusting this value in production.
    traces_sample_rate=1.0,
    send_default_pii=True,
)

INSTALLED_APPS = [
    "daphne",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.gis",
    # Third party app
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
    # Internal apps
    "users_api",
    "community_api",
    "machine_api",
    "competition_api",
    "notification",
    "marketplace",
]


private_key = str.encode(env("private_key"))
private_key = base64.b64decode(private_key).decode("utf-8")

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
cred = credentials.Certificate(cert)
FIREBASE_APP = initialize_app(cred)

FCM_DJANGO_SETTINGS = {
    # an instance of firebase_admin.App to be used as default for all fcm-django requests
    # default: None (the default Firebase app)
    "DEFAULT_FIREBASE_APP": FIREBASE_APP,
    "APP_VERBOSE_NAME": "notification",
    # true if you want to have only one active device per registered user at a time
    # default: False
    "ONE_DEVICE_PER_USER": False,
    # devices to which notifications cannot be sent,
    # are deleted upon receiving error response from FCM
    # default: False
    "DELETE_INACTIVE_DEVICES": False,
    # Transform create of an existing Device (based on registration id) into
    # an update. See the section
    # "Update of device with duplicate registration ID" for more details.
    # default: False
    "UPDATE_ON_DUPLICATE_REG_ID": True,
}

AUTHENTICATION_BACKENDS = ["core.backends.AuthBackend"]

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.BasicAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Dropme Project api",
    "VERSION": "1.0.0",
    "SWAGGER_UI_DIST": "SIDECAR",
    "SWAGGER_UI_FAVICON_HREF": "SIDECAR",
}

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    },
}

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.db.DatabaseCache",
        "LOCATION": "cache_table",
    }
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=10),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "TOKEN_OBTAIN_SERIALIZER": "users_api.serializers.MyTokenObtainPairSerializer",
    "TOKEN_REFRESH_SERIALIZER": "rest_framework_simplejwt.serializers.TokenRefreshSerializer",
    "TOKEN_VERIFY_SERIALIZER": "rest_framework_simplejwt.serializers.TokenVerifySerializer",
    "TOKEN_BLACKLIST_SERIALIZER": "rest_framework_simplejwt.serializers.TokenBlacklistSerializer",
    "USER_AUTHENTICATION_RULE": "core.backends.simple_jwt_authentication_rule",
}


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

ASGI_APPLICATION = "core.asgi.application"
# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.contrib.gis.db.backends.postgis",
        "HOST": env("db_host"),
        "NAME": env("db_name"),
        "PASSWORD": env("db_password"),
        "PORT": int(env("db_port")),
        "USER": "postgres",
    }
}

DATA_UPLOAD_MAX_MEMORY_SIZE = 10485760
FILE_UPLOAD_MAX_MEMORY_SIZE = 10485760

if os.name == "nt":
    import platform

    OSGEO4W = r"C:\OSGeo4W"
    if "64" in platform.architecture()[0]:
        # OSGEO4W += "64"
        pass

    assert os.path.isdir(OSGEO4W), "Directory does not exist: " + OSGEO4W
    os.environ["OSGEO4W_ROOT"] = OSGEO4W
    os.environ["GDAL_DATA"] = "C:\Program Files\GDAL\gdal-data"
    os.environ["PROJ_LIB"] = OSGEO4W + r"\share\proj"
    GDAL_LIBRARY_PATH = r"C:\OSGeo4W\bin\gdal306"
    os.environ["PATH"] = OSGEO4W + r"\bin;" + os.environ["PATH"]

# GDAL_LIBRARY_PATH = r'C:\OSGeo4W\bin\gdal306.dll'


AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


LANGUAGE_CODE = "en"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True

LANGUAGES = [
    ("en", _("English")),
    ("ar", _("Arabic")),
]

LOCALE_PATHS = [
    BASE_DIR / "locale/",
]

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# sending email configuration
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.zoho.com"
EMAIL_USE_SSL = False
EMAIL_USE_TLS = True
EMAIL_PORT = 587
EMAIL_HOST_USER = env("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD")

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

if DEBUG:
    env.read_env(BASE_DIR / ".env.local")
    DATABASES = {
        "default": {
            "ENGINE": "django.contrib.gis.db.backends.postgis",
            "HOST": env("local_db_host"),
            "NAME": env("local_db_name"),
            "PASSWORD": env("local_db_password"),
            "PORT": int(env("local_db_port")),
            "USER": env("local_db_user"),
        },
    }
    MEDIA_ROOT = BASE_DIR / "media"
    MEDIA_URL = "/media/"
else:
    DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
    AWS_S3_REGION_NAME = env("AWS_S3_REGION_NAME")
    AWS_S3_ENDPOINT_URL = f"https://s3.{AWS_S3_REGION_NAME}.backblazeb2.com"
    AWS_ACCESS_KEY_ID = env("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = env("AWS_SECRET_ACCESS_KEY")
    AWS_STORAGE_BUCKET_NAME = env("AWS_STORAGE_BUCKET_NAME")
