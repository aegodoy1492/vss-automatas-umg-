@echo off
echo ============================================================
echo   VENTURA SOFTWARE SOLUTIONS (VSS) - INICIAR PLATAFORMA
echo ============================================================
echo.

start "VSS Backend" cmd /k "cd /d C:\DESARROLLO\VSS\AUTOMATAS\BACKEND && venv\Scripts\python.exe -m uvicorn app.main:app --reload"

timeout /t 3 /nobreak >nul

start "VSS Frontend" cmd /k "cd /d C:\DESARROLLO\VSS\AUTOMATAS\frontend && npm run dev"

timeout /t 4 /nobreak >nul

start "" "http://localhost:5173"

echo.
echo Backend y frontend se abrieron en dos ventanas nuevas.
echo No las cierres mientras uses la plataforma.
echo.
pause
