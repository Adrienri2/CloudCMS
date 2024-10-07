"""
ASGI config for cloudcms project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

# Configura la variable de entorno DJANGO_SETTINGS_MODULE.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cloudcms.settings')

# Crea una aplicación ASGI que utilizará la configuración de Django.
application = get_asgi_application()
