#!/bin/bash

# Aplicar migraciones y recopilar archivos estáticos
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic --noinput

# Iniciar Gunicorn en segundo plano con 1 trabajador
gunicorn cloudcms.wsgi --log-file - --workers=1 &

# Iniciar el worker de Celery en primer plano con concurrencia limitada
celery -A cloudcms worker --loglevel=info --concurrency=1
