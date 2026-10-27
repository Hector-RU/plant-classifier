"""ASGI entry point for the plant classifier."""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'plant_classifier.settings')

application = get_asgi_application()
