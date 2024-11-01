#!/bin/bash

# Aplicar migraciones y recopilar archivos estáticos
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic --noinput

# Iniciar Gunicorn en segundo plano con 1 trabajador
gunicorn cloudcms.wsgi --log-file - --workers=1 &

# Ejecutar el worker de Celery en segundo plano
nohup celery -A cloudcms worker --loglevel=info --concurrency=1

# Ejecutar el beat scheduler de Celery en segundo plano
nohup celery -A cloudcms beat --loglevel=info &
