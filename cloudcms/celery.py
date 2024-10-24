from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab

# Establece el módulo de configuración de Django para Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cloudcms.settings')

app = Celery('cloudcms')

# Usa una cadena aquí para que los trabajadores no necesiten serializar
# el objeto de configuración en cada tarea
app.config_from_object('django.conf:settings', namespace='CELERY')

# Descubre tareas en todos los paquetes de aplicaciones Django
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'publish-scheduled-blogs-every-minute': {
        'task': 'blogs.tasks.publish_scheduled_blogs',
        'schedule': crontab(minute='*/1'),  # Ejecutar cada minuto
    },
     'expire-scheduled-blogs-every-minute': {
        'task': 'blogs.tasks.expire_scheduled_blogs',
        'schedule': crontab(minute='*/1'),  # Ejecutar cada minuto
    },
}