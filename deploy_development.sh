#!/bin/bash
# Terminar cualquier proceso que esté utilizando el puerto 8000
echo "Terminando procesos en el puerto 8000..."
sudo fuser -k 8000/tcp

# Configurar variables de entorno para desarrollo en el archivo .env
echo "Configurando variables de entorno para desarrollo..."
sed -i 's/^DEBUG=.*/DEBUG=True/' .env

# Añadir 'DEBUG=True' al archivo .env si no existe
echo "Verificando si 'DEBUG=True' está en .env..."
grep -qxF 'DEBUG=True' .env || echo 'DEBUG=True' >> .env

# Cargar variables de entorno desde .env
echo "Cargando variables de entorno desde .env..."
export $(cat .env | xargs)

# Actualización y corrección de paquetes faltantes
echo "Actualizando paquetes y corrigiendo problemas de instalación..."
sudo apt update --fix-missing
sudo apt upgrade -y

# Instalación de dependencias del sistema
echo "Instalando dependencias del sistema..."
sudo apt install -y python3-pip python3-virtualenv redis-server postgresql postgresql-contrib

# Configuración de PostgreSQL
echo "Configurando PostgreSQL..."
sudo -u postgres psql <<EOF
-- Eliminar las bases de datos si existen
DROP DATABASE IF EXISTS dbcloudcms_dev;
DROP DATABASE IF EXISTS dbcloudcms_prod;

-- Eliminar el usuario si existe
DROP USER IF EXISTS admin_cms;

-- Crear el usuario y las bases de datos
CREATE USER admin_cms WITH PASSWORD '1234';
CREATE DATABASE dbcloudcms_dev OWNER admin_cms;
CREATE DATABASE dbcloudcms_prod OWNER admin_cms;
ALTER USER admin_cms CREATEDB;
EOF

# Crear y activar el entorno virtual
echo "Creando y activando el entorno virtual..."
virtualenv entorno1
source entorno1/bin/activate

# Instalar dependencias en el entorno virtual
echo "Instalando dependencias en el entorno virtual..."
pip install -r requirements.txt

# Migrar la base de datos
echo "Realizando migraciones de la base de datos..."
python manage.py makemigrations
python manage.py migrate

# Ejecutar el worker de Celery en segundo plano
echo "Ejecutando el worker de Celery en segundo plano..."
nohup celery -A cloudcms worker --loglevel=info &

# Ejecutar el beat scheduler de Celery en segundo plano
echo "Ejecutando el beat scheduler de Celery en segundo plano..."
nohup celery -A cloudcms beat --loglevel=info &

# Ejecutar el servidor en modo desarrollo
echo "Iniciando el servidor en modo desarrollo..."
python manage.py runserver
