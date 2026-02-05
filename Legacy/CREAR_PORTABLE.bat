@echo off
title VultrDrive - Crear Version Portable
echo ==========================================
echo   VultrDrive Desktop - Empaquetador
echo ==========================================
echo.
echo Este script creara una version portable con
echo todas tus credenciales y configuraciones.
echo.
echo Presiona cualquier tecla para continuar...
pause > nul
echo.
echo Ejecutando empaquetador...
powershell -ExecutionPolicy Bypass -File "%~dp0scripts\EMPAQUETAR.ps1"
echo.
echo Proceso terminado.
pause
