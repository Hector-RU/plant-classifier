"""WSGI entry point for the plant classifier."""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'plant_classifier.settings')

application = get_wsgi_application()
