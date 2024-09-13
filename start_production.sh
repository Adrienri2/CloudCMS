#!/bin/bash

# Terminar cualquier proceso que esté utilizando el puerto 8000
sudo fuser -k 8000/tcp

# Crear un alias para python3.10
#alias python='python3.10'
#alias pip='python3.10 -m pip'

# Configurar variables de entorno para producción en el archivo .env
sed -i 's/^DEBUG=.*/DEBUG=False/' .env

# Añadir las variables si no existen
grep -qxF 'DEBUG=False' .env || echo 'DEBUG=False' >> .env

# Cargar variables de entorno desde .env
export $(cat .env | xargs)

# Recolectar archivos estáticos
python manage.py collectstatic --noinput

# Reiniciar Nginx y Gunicorn
sudo nginx -t
sudo systemctl restart nginx
#sudo systemctl restart gunicorn

# Migrar la base de datos
#python manage.py makemigrations
#python manage.py migrate

# Ejecutar Gunicorn en modo producción
#python manage.py runserver --insecure

#gunicorn --workers 3 --bind 127.0.0.1:8000 cloudcms.wsgi:application
#gunicorn --workers 3 --bind 127.0.0.1:8000 --log-level debug --error-logfile - --access-logfile - cloudcms.wsgi:application
#gunicorn --workers 3 --bind 127.0.0.1:8000 --log-level info --error-logfile - --access-logfile - cloudcms.wsgi:application
gunicorn -c gunicorn.conf.py cloudcms.wsgi:application