@echo off
SETLOCAL

REM Verificar si Node.js está instalado
where node >nul 2>nul
IF %ERRORLEVEL% NEQ 0 (
    echo Node.js no esta instalado. Instalandolo ahora...
    powershell -Command "Start-Process 'https://nodejs.org/dist/v18.17.1/node-v18.17.1-x64.msi' -Wait"
    IF %ERRORLEVEL% NEQ 0 (
        echo Error al instalar Node.js. Abortando.
        exit /b 1
    )
) ELSE (
    echo Node.js ya esta instalado.
)

REM Verificar si Railway CLI está instalado
where railway >nul 2>nul
IF %ERRORLEVEL% NEQ 0 (
    echo Railway CLI no esta instalado. Instalandolo ahora...
    npm install -g railway
    IF %ERRORLEVEL% NEQ 0 (
        echo Error al instalar Railway CLI. Abortando.
        exit /b 1
    )
) ELSE (
    echo Railway CLI ya esta instalado.
)

IF EXIST "%USERPROFILE%\CloudCMS" (
    rmdir /S /Q "%USERPROFILE%\CloudCMS"
)
mkdir "%USERPROFILE%\CloudCMS"

IF EXIST "%USERPROFILE%\CarpetaVacia" (
    rmdir /S /Q "%USERPROFILE%\CarpetaVacia"
)
mkdir "%USERPROFILE%\CarpetaVacia"
git clone --branch adrian --single-branch --depth 1 https://github.com/Adrienri2/CloudCMS %USERPROFILE%\CloudCMS

REM Variables para el proyecto
SET "PROJECT_NAME=cloudcms"
SET "PROJECT_PATH=%USERPROFILE%\CloudCMS"
SET "EMPTY_SERVICE_PATH=%USERPROFILE%\CarpetaVacia"
SET "ENV_PATH=%PROJECT_PATH%\.env"  REM Ruta al archivo .env

REM Iniciar sesión en Railway
echo Iniciando sesion en Railway...
railway login
IF %ERRORLEVEL% NEQ 0 (
    echo Error al iniciar sesion en Railway. Abortando.
    exit /b 1
)

REM Verificar si el proyecto ya existe y vincularlo
echo Verificando si el proyecto %PROJECT_NAME% ya existe en Railway...
railway list | findstr /i %PROJECT_NAME% >nul
IF %ERRORLEVEL% EQU 0 (
    echo El proyecto %PROJECT_NAME% ya existe. Vinculandolo ahora...
    railway link --project %PROJECT_NAME%
) ELSE (
    REM Crear el proyecto en Railway con el nombre especificado
    echo Creando el proyecto %PROJECT_NAME% en Railway...
    railway init --name %PROJECT_NAME%
    
    REM Cambiar al proyecto recién creado
    echo Cambiando al proyecto %PROJECT_NAME%...
    railway link --project %PROJECT_NAME%

    echo Proyecto %PROJECT_NAME% creado y vinculado exitosamente.
)

REM Crear el servicio vacío
echo Creando un servicio vacio en Railway desde %EMPTY_SERVICE_PATH%...
railway up %EMPTY_SERVICE_PATH%

REM Agregar el servicio de PostgreSQL
echo Agregando el servicio de PostgreSQL en Railway...
railway add --database postgres

REM Agregar el servicio de Redis
echo Agregando el servicio de Redis en Railway...
railway add --database redis

REM Vincular explícitamente el servicio
echo Vinculando el servicio %PROJECT_NAME%...
railway service %PROJECT_NAME%

REM Esperar unos segundos para asegurar que el dominio esté disponible
timeout /t 10 /nobreak >nul

REM Cargar variables de entorno desde el archivo .env en Railway
echo Cargando variables de entorno desde %ENV_PATH% en Railway...
FOR /F "tokens=1,2 delims==" %%G IN ('type "%ENV_PATH%"') DO (
    railway variables --set "%%G=%%H"
)

REM Intentar obtener el dominio generado por Railway
echo Obteniendo el dominio generado por Railway...
FOR /F "tokens=2 delims= " %%D IN ('railway domain --json ^| findstr /i "https://"') DO (
    SET DOMAIN=%%D
)
SET DOMAIN=%DOMAIN:"=%

REM Imprimir el dominio en la consola
echo Dominio generado: %DOMAIN%

REM Eliminar "https://" del dominio
SET DOMAIN=%DOMAIN:https://=%

REM Configurar ALLOWED_HOSTS en Railway usando el dominio recuperado
echo Configurando ALLOWED_HOSTS con el dominio %DOMAIN%...
railway variables --set "ALLOWED_HOSTS=127.0.0.1,localhost,%DOMAIN%"

REM Desplegar el proyecto en Railway desde la ruta especificada
echo Realizando despliegue final desde %PROJECT_PATH% en Railway...
railway up %PROJECT_PATH%

ENDLOCAL
pause
