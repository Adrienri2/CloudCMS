"""
WSGI config for cloudcms project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""


import os

from django.core.wsgi import get_wsgi_application

# Configura la variable de entorno DJANGO_SETTINGS_MODULE.
# Esto le dice a Django qué archivo de configuración usar.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cloudcms.settings')

# Crea una aplicación WSGI que utilizará la configuración de Django.
# Esta es la interfaz entre el servidor web y tu aplicación Django.
application = get_wsgi_application()

# Notas adicionales:
# - Este archivo es utilizado por servidores WSGI como Gunicorn o uWSGI en producción.
# - En un entorno de desarrollo, el servidor de desarrollo de Django no utiliza este archivo.
# - Si necesitas realizar alguna configuración adicional antes de que se inicie la aplicación,
#   puedes hacerlo en es