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
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
