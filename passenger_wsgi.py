import os
import sys

# Path to your project root (adjust if needed)
sys.path.insert(0, os.path.dirname(__file__))

# Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
