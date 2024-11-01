#!/bin/bash

# Terminar cualquier proceso que esté utilizando el puerto 8000
sudo fuser -k 8000/tcp

# Configurar variables de entorno para desarrollo en el archivo .env
sed -i 's/^DEBUG=.*/DEBUG=True/' .env

# Añadir las variables si no existen
grep -qxF 'DEBUG=True' .env || echo 'DEBUG=True' >> .env

# Cargar variables de entorno desde .env
export $(cat .env | xargs)

# Migrar la base de datos
python manage.py makemigrations
python manage.py migrate


# Ejecutar el worker de Celery en segundo plano
nohup celery -A cloudcms worker --loglevel=info &

# Ejecutar el beat scheduler de Celery en segundo plano
nohup celery -A cloudcms beat --loglevel=info &

# Ejecutar el servidor en modo desarrollo
python manage.py runserver