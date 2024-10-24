#!/bin/bash

# Aplicar migraciones y recopilar archivos estáticos
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic --noinput

# Iniciar Gunicorn en segundo plano
gunicorn cloudcms.wsgi --log-file - &

# Iniciar el worker de Celery en primer plano
celery -A cloudcms worker --loglevel=info
