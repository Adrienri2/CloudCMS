## Instalación

1. Actualizar y corregir paquetes faltantes:
    ```sh
    sudo apt update --fix-missing
    ```

2. Actualizar paquetes:
    ```sh
    sudo apt upgrade
    ```

3. Instalar `python3-pip`:
    ```sh
    sudo apt install python3-pip
    ```

4. Instalar `nginx`:
    ```sh
    sudo apt install nginx
    ```

5. Instalar `virtualenv` para crear entornos virtuales:
    ```sh
    sudo apt install python3-virtualenv
    ```

6. Instalar `redis-server`:
    ```sh
    sudo apt-get install redis-server
    ```

7. Crear un entorno virtual:
    ```sh
    virtualenv entorno1
    ```

8. Activar el entorno virtual:
    ```sh
    source entorno1/bin/activate
    ```

9. Instalar las dependencias en el entorno virtual:
    ```sh
    pip install -r requirements.txt
    ```

10. Otorgar permisos a los scripts:
    ```sh
    chmod +x start_production.sh start_development.sh
    ```

## Configuración de PostgreSQL

1. Instalar PostgreSQL si no está instalado:
    ```sh
    sudo apt install postgresql postgresql-contrib
    ```

2. Conéctate a PostgreSQL como el usuario `postgres`:
    ```sh
    sudo -u postgres psql
    ```

3. Dentro de `psql`, ejecuta los siguientes comandos:

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

    - Otorgar permisos de creación de bases de datos al usuario:
        ```sql
        ALTER USER admin_cms CREATEDB;
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

2. Asignarle el rol de admin al superusario:
    ```sh
    python manage.py shell
    from accounts.models import User
    # Obtén el usuario
    user = User.objects.get(username='nombre_de_usuario')  # Reemplaza 'nombre_de_usuario' con el nombre de usuario real
    # Asigna el rol de admin
    user.role = 'admin'
    user.save()
    print(f"El usuario {user.username} ahora tiene el rol de {user.role}.")
    exit()
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
    python manage.py test accounts.tests.LoginViewTests
    python manage.py test accounts.tests.UserListViewTests
    python manage.py test accounts.tests.EditUserViewTests

    python manage.py test blogs.tests.BlogViewTests
    python manage.py test blogs.tests.CreateBookmarkTests
    python manage.py test blogs.tests.CreateLikeTests
    python manage.py test blogs.tests.MarkAsReadViewTests
    python manage.py test blogs.tests.ToggleFavoriteCategoryViewTests
    python manage.py test blogs.tests.PagoViewTests
    python manage.py test blogs.tests.BlogStatisticsViewTests

    python manage.py test management.tests.KanbanViewTest
    ```

## API

- La API estará disponible en: [http://localhost:8000/swagger/](http://localhost:8000/swagger/)