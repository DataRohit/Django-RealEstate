from realestate.settings.base import *


# Set the debug status
DEBUG = False
TEMPLATE_DEBUG = False

# Database
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "realestate" / "database" / "db.sqlite3",
    }
}
