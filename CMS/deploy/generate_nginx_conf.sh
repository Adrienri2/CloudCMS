#!/bin/bash

# Obtener la ruta del directorio del proyecto
PROJECT_DIR=$(pwd)

# Crear el archivo de configuración de Nginx
cat <<EOL > cloudcms_nginx.conf
server {
    listen 80;
    server_name localhost;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /static/ {
        alias $PROJECT_DIR/static_prod/;
    }

    location /uploads/ {
        alias $PROJECT_DIR/uploads/;
    }

    error_log /var/log/nginx/cloudcms_error.log;
    access_log /var/log/nginx/cloudcms_access.log;
}
EOL
