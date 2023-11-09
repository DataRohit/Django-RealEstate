# Import base settings
from realestate.settings.base import *


# Set the debug status
DEBUG = False
TEMPLATE_DEBUG = False


# Database
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "database" / "db.sqlite3",
    }
}


# Set the email backend service
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = os.environ["EMAIL_HOST"]
EMAIL_HOST_USER = os.environ["EMAIL_HOST_USER"]
EMAIL_HOST_PASSWORD = os.environ["EMAIL_HOST_PASSWORD"]
EMAIL_PORT = os.environ["EMAIL_PORT"]
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False
