@echo off
title VultrDrive Desktop
cd /d "%~dp0"
echo =======================================
echo   VultrDrive Desktop - Iniciando...
echo =======================================
echo.
echo Verificando dependencias...
pip install -r requirements.txt -q 2>nul
echo.
echo Iniciando aplicacion...
py app.py
if %ERRORLEVEL% neq 0 (
    echo.
    echo [ERROR] La aplicacion se cerro con un error.
    echo Revisa los logs en la carpeta "logs" para mas informacion.
    echo.
    pause
)
