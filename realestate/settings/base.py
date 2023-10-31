# Imports
from pathlib import Path
import datetime


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "^9u7w-_o(@^r@(@)h1qdl*d6h+)zuo)x_9_k8n)ig82ds0#am-"


# Allowed hosts list
ALLOWED_HOSTS = ["localhost", "127.0.0.1", ".vercel.app"]


# Set the User model
AUTH_USER_MODEL = "appauth.User"


# Installed apps list
INSTALLED_APPS = [
    # Dfault apps
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework_simplejwt",
    # Third party apps
    "django_extensions",
    "django_bootstrap5",
    # Real Estate apps
    "realestate.apps.appauth",
    "realestate.apps.core",
    "realestate.apps.pending",
]


# Middleware list
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


# Root URL configuration
ROOT_URLCONF = "realestate.urls"


# Template configuration
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


# WSGI application
WSGI_APPLICATION = "realestate.wsgi.app"


# Internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Kolkata"
USE_I18N = True
USE_L10N = True
USE_TZ = True


# Base path for static files
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles" / "static"


# Default auto field
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# Customize logging
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "django": {
            "format": "{levelname:8s} {asctime:25s} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "django",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "DEBUG",
    },
    "loggers": {
        "django.server": {
            "handlers": ["console"],
            "level": "INFO",
        },
    },
}


# Login redirect URL
LOGIN_REDIRECT_URL = "home"
LOGIN_URL = "login"


# REST API settings
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.BasicAuthentication",
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.LimitOffsetPagination",
    "PAGE_SIZE": 10,
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {"anon": "1000/hour", "user": "1000/hour"},
}


# JWT settings
SIMPLE_JWT = {
    "AUTH_HEADER_TYPES": ["JWT"],
    "ACCESS_TOKEN_LIFETIME": datetime.timedelta(minutes=1),
    "REFRESH_TOKEN_LIFETIME": datetime.timedelta(minutes=2),
    "SIGNING_KEY": "5e7e54898831d5fe9a2feaa08af07b5682415dde9342d6f754418f31ca4f328d",
    "JWT_PAYLOAD_HANDLER": "realestate.apps.appauth.utils.jwt_payload_handler",
    "JWT_RESPONSE_PAYLOAD_HANDLER": "realestate.apps.appauth.utils.jwt_response_payload_handler",
}
