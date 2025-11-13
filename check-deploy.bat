@echo off
echo ========================================
echo   Verificacion de Configuracion Docker
echo ========================================
echo.

echo Verificando archivos necesarios...
echo.

if not exist "Dockerfile" (
    echo [X] Dockerfile - NO ENCONTRADO
    set /a errors+=1
) else (
    echo [OK] Dockerfile
)

if not exist "requirements.txt" (
    echo [X] requirements.txt - NO ENCONTRADO
    set /a errors+=1
) else (
    echo [OK] requirements.txt
)

if not exist "railway.json" (
    echo [X] railway.json - NO ENCONTRADO
    set /a errors+=1
) else (
    echo [OK] railway.json
)

if not exist ".dockerignore" (
    echo [X] .dockerignore - NO ENCONTRADO
    set /a errors+=1
) else (
    echo [OK] .dockerignore
)

if not exist ".env.example" (
    echo [X] .env.example - NO ENCONTRADO
    set /a errors+=1
) else (
    echo [OK] .env.example
)

if not exist "manage.py" (
    echo [X] manage.py - NO ENCONTRADO
    set /a errors+=1
) else (
    echo [OK] manage.py
)

echo.
echo Verificando dependencias en requirements.txt...
echo.

findstr /C:"gunicorn" requirements.txt >nul
if errorlevel 1 (
    echo [X] gunicorn - NO ENCONTRADO en requirements.txt
    set /a errors+=1
) else (
    echo [OK] gunicorn
)

findstr /C:"python-decouple" requirements.txt >nul
if errorlevel 1 (
    echo [X] python-decouple - NO ENCONTRADO en requirements.txt
    set /a errors+=1
) else (
    echo [OK] python-decouple
)

findstr /C:"whitenoise" requirements.txt >nul
if errorlevel 1 (
    echo [X] whitenoise - NO ENCONTRADO en requirements.txt
    set /a errors+=1
) else (
    echo [OK] whitenoise
)

findstr /C:"stripe" requirements.txt >nul
if errorlevel 1 (
    echo [X] stripe - NO ENCONTRADO en requirements.txt
    set /a errors+=1
) else (
    echo [OK] stripe
)

findstr /C:"dj-database-url" requirements.txt >nul
if errorlevel 1 (
    echo [X] dj-database-url - NO ENCONTRADO en requirements.txt
    set /a errors+=1
) else (
    echo [OK] dj-database-url
)

echo.
echo ========================================
echo   Resumen
echo ========================================
echo.

if defined errors (
    echo [!] Se encontraron %errors% errores
    echo     Por favor, corrige los problemas antes de desplegar
    echo.
) else (
    echo [OK] Todo listo para desplegar!
    echo.
    echo Proximos pasos:
    echo 1. Crear proyecto en Railway.app
    echo 2. Agregar PostgreSQL database
    echo 3. Configurar variables de entorno
    echo 4. Conectar repositorio de GitHub
    echo 5. Railway desplegara automaticamente
    echo.
    echo Ver DEPLOY.md para instrucciones detalladas
)

echo.
pause
