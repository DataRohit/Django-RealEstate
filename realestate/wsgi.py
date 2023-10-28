# Imports
import os
from django.core.wsgi import get_wsgi_application


# Set the default settings module for the 'wsgi' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "realestate.settings.dev")


# Initialize the WSGI application used by Django.
app = get_wsgi_application()
