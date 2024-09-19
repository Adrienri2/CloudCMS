# CloudCMS

## Instalación

1. Instalar `python3-pip`:
    ```sh
    sudo apt install python3-pip
    ```

2. Instalar `nginx`:
    ```sh
    sudo apt install nginx-full=1.18.0-6ubuntu14.4
    ```

3. Instalar `virtualenv` para crear entornos virtuales:
    ```sh
    pip install virtualenv
    ```

4. Crear un entorno virtual:
    ```sh
    virtualenv entorno1
    ```

5. Instalar las dependencias en el entorno virtual:
    ```sh
    pip install -r requirements.txt
    ```

6. Otorgar permisos a los scripts:
    ```sh
    chmod +x start_production.sh start_development.sh
    ```

## Configuración de PostgreSQL

1. Conéctate a PostgreSQL como el usuario `postgres`:
    ```sh
    sudo -u postgres psql
    ```

2. Dentro de `psql`, ejecuta los siguientes comandos:

    - Crear el usuario:
        ```sql
        CREATE USER admin_cms WITH PASSWORD '1234';
        ```

    - Crear la base de datos para desarrollo:
        ```sql
        CREATE DATABASE dbcloudcms_dev OWNER admin_cms;
        ```

    - Crear la base de datos para producción:
        ```sql
        CREATE DATABASE dbcloudcms_prod OWNER admin_cms;
        ```

    - Salir de [`psql`]:
        ```sh
        \q
        ```

## Migraciones y Superusuario

1. Ejecutar migraciones:
    ```sh
    python manage.py makemigrations
    python manage.py migrate
    ```

2. Crear un superusuario:
    ```sh
    python manage.py createsuperuser
    ```

## Ejecución de Scripts

1. Ejecutar los scripts:
    ```sh
    ./start_production.sh
    ./start_development.sh
    ```

## Documentación

1. Generar la documentación:
    ```sh
    cd docs
    make html
    ```

## Pruebas

1. Ejecutar las pruebas:
    ```sh
    python manage.py test accounts.tests
    python manage.py test blogs.tests
    ```

## API

- La API estará disponible en: [http://localhost:8000/swagger/](http://localhost:8000/swagger/)

# a