#!/bin/bash

# Terminar cualquier proceso que esté utilizando el puerto 8000
sudo fuser -k 8000/tcp

# Activar el entorno virtual
source entorno1/bin/activate

# Asegurar permisos correctos para los archivos estáticos y el directorio del proyecto
sudo chmod o+x /home/$USER
sudo chmod o+x /home/$USER/CloudCMS
sudo chown -R www-data:www-data $(pwd)/static_prod/
sudo chown -R $USER:$USER $(pwd)/static_prod/
sudo chmod -R 755 $(pwd)/static_prod/
sudo chmod -R o+rX $(pwd)/static_prod/

# Configurar Nginx para servir la aplicación Django
sudo tee /etc/nginx/sites-available/django_project > /dev/null <<EOL
server {
    listen 80;
    server_name 127.0.0.1;
    client_max_body_size 100M;
    location /static/ {
        alias $(pwd)/static_prod/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOL

# Crear un enlace simbólico para habilitar el sitio en Nginx
sudo ln -sf /etc/nginx/sites-available/django_project /etc/nginx/sites-enabled

# Probar la configuración de Nginx
sudo nginx -t

# Reiniciar Nginx para aplicar la nueva configuración
sudo systemctl restart nginx

# Configurar variables de entorno para producción en el archivo .env
sed -i 's/^DEBUG=.*/DEBUG=False/' .env

# Añadir las variables si no existen
grep -qxF 'DEBUG=False' .env || echo 'DEBUG=False' >> .env

# Cargar variables de entorno desde .env
export $(cat .env | xargs)

# Recolectar archivos estáticos
python manage.py collectstatic --noinput

# Aplicar migraciones de la base de datos
python manage.py migrate

# Ejecutar el worker de Celery en segundo plano
nohup celery -A cloudcms worker --loglevel=info &

# Ejecutar el beat scheduler de Celery en segundo plano
nohup celery -A cloudcms beat --loglevel=info &

# Iniciar Gunicorn con la configuración especificada
gunicorn --pythonpath $(pwd) --bind 127.0.0.1:8000 --workers 3 cloudcms.wsgi:application