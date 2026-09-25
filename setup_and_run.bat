@echo off
TITLE Instalador y Lanzador - Proyecto Automatas VSS
echo ============================================================
echo   VENTURA SOFTWARE SOLUTIONS (VSS) - SETUP AUTOMATAS
echo ============================================================
echo.

:: 1. Configuracion del Entorno Virtual de Python
echo [1/6] Creando entorno virtual de Python...
python -m venv venv --without-pip
if %errorlevel% neq 0 (
    echo Error al crear el entorno virtual.
    pause
    exit /b
)

echo [2/6] Instalando pip en el entorno virtual...
.\venv\Scripts\python.exe -m ensurepip --upgrade

echo [3/6] Instalando dependencias de Python (requirements.txt)...
.\venv\Scripts\python.exe -m pip install -r requirements.txt

:: 2. Ejecucion de Pruebas Unitarias
echo [4/6] Ejecutando pruebas unitarias con Pytest...
.\venv\Scripts\python.exe -m pytest -q
if %errorlevel% neq 0 (
    echo.
    echo [ADVERTENCIA] Algunas pruebas han fallado. Revisa los mensajes anteriores.
    pause
)

:: 3. Instalacion de Dependencias de Frontend
echo [5/6] Instalando dependencias Node.js (npm install)...
call npm install

:: 4. Lanzamiento de Servicios y Paginas Web
echo.
echo [6/6] Iniciando servidores y abriendo navegador...
echo ============================================================

:: Iniciar Backend en una nueva ventana de consola
start "VSS - Backend (Uvicorn)" cmd /k ".\venv\Scripts\python.exe -m uvicorn app.main:app --reload"

:: Esperar 3 segundos para asegurar que el backend levante
timeout /t 3 /nobreak >nul

:: Abrir Documentacion API Swagger
start http://localhost:8000/docs

:: Iniciar Frontend en una nueva ventana de consola
start "VSS - Frontend (Vite/React)" cmd /k "npm run dev"

:: Esperar 3 segundos para asegurar que el servidor de desarrollo levante
timeout /t 3 /nobreak >nul

:: Abrir Aplicacion Web Frontend
start http://localhost:5173

echo.
echo ============================================================
echo   INSTALACION Y EJECUCION COMPLETADA CON EXITO
echo ============================================================
echo.
pause