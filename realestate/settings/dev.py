# Import base settings
from realestate.settings.base import *


# Set the debug status
DEBUG = True
TEMPLATE_DEBUG = True


# Database
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "database" / "db.sqlite3",
    }
}


# Set the email backend service
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
