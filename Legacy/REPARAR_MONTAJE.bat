@echo off
title Reparador de Vultr Drive
color 1f
echo ===================================================
echo      HERRAMIENTA DE REPARACION VULTR DRIVE
echo ===================================================
echo.
echo 1. Cerrando procesos rclone...
taskkill /F /IM rclone.exe /T >nul 2>&1
echo    [OK] Procesos cerrados.
echo.

echo 2. Limpiando cache temporal de rclone...
echo    Esto eliminara archivos pendientes de subida corruptos.
rmdir /S /Q "%LOCALAPPDATA%\rclone" >nul 2>&1
rmdir /S /Q "%TEMP%\rclone" >nul 2>&1
echo    [OK] Cache limpiado.
echo.

echo 3. Reiniciando Explorador de Windows (opcional)...
echo    A veces necesario para limpiar letras de unidad fantasmas.
taskkill /f /im explorer.exe >nul 2>&1
start explorer.exe
echo    [OK] Explorador reiniciado.
echo.

echo ===================================================
echo      REPARACION COMPLETADA
echo ===================================================
echo.
echo Por favor, abre Vultr Drive Desktop e intenta montar de nuevo.
echo.
pause
