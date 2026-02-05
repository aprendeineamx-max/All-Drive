@echo off
chcp 65001 >nul
color 0B
title Instalador Automático de WinFsp

echo.
echo ═══════════════════════════════════════════════════════════════
echo           INSTALADOR AUTOMATICO DE WINFSP
echo ═══════════════════════════════════════════════════════════════
echo.
echo WinFsp es REQUERIDO para montar unidades en Windows.
echo Es gratuito, de código abierto y seguro.
echo.
echo Este script:
echo   [1] Descargará WinFsp desde GitHub oficial
echo   [2] Lo instalará automáticamente
echo   [3] Verificará la instalación
echo.
echo ═══════════════════════════════════════════════════════════════
echo.

:: Verificar si ya está instalado
if exist "C:\Program Files (x86)\WinFsp\bin\winfsp-x64.dll" (
    echo ✓ WinFsp YA ESTA INSTALADO
    echo.
    echo Ubicación: C:\Program Files (x86)\WinFsp
    echo.
    echo No necesitas hacer nada más. Ya puedes montar unidades.
    echo.
    pause
    exit /b 0
)

echo [Paso 1/3] Descargando WinFsp...
echo.
echo URL: https://github.com/winfsp/winfsp/releases/download/v2.0/winfsp-2.0.23075.msi
echo Tamaño: ~2 MB
echo.

:: Crear carpeta temporal
set "TEMP_DIR=%TEMP%\VultrDrive_WinFsp"
if not exist "%TEMP_DIR%" mkdir "%TEMP_DIR%"

:: Descargar WinFsp usando PowerShell
powershell -Command "& { [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; $ProgressPreference = 'SilentlyContinue'; Invoke-WebRequest -Uri 'https://github.com/winfsp/winfsp/releases/download/v2.0/winfsp-2.0.23075.msi' -OutFile '%TEMP_DIR%\winfsp.msi' }"

if not exist "%TEMP_DIR%\winfsp.msi" (
    echo.
    echo ✗ ERROR: No se pudo descargar WinFsp
    echo.
    echo SOLUCIÓN MANUAL:
    echo   1. Descarga desde: https://winfsp.dev/rel/
    echo   2. Instala: winfsp-2.0.23075.msi
    echo   3. Reinicia VultrDriveDesktop
    echo.
    pause
    exit /b 1
)

echo ✓ Descarga completada
echo.
echo [Paso 2/3] Instalando WinFsp...
echo.
echo NOTA: Puede aparecer una ventana de UAC pidiendo permisos.
echo       Haz clic en "Sí" para continuar.
echo.
timeout /t 3 /nobreak >nul

:: Instalar WinFsp silenciosamente
msiexec /i "%TEMP_DIR%\winfsp.msi" /qn /norestart

:: Esperar a que termine la instalación
timeout /t 5 /nobreak >nul

echo.
echo [Paso 3/3] Verificando instalación...
echo.

:: Verificar instalación
if exist "C:\Program Files (x86)\WinFsp\bin\winfsp-x64.dll" (
    echo ✓ ¡INSTALACION EXITOSA!
    echo.
    echo WinFsp se instaló correctamente en:
    echo   C:\Program Files (x86)\WinFsp
    echo.
    echo ═══════════════════════════════════════════════════════════════
    echo                      ¡LISTO!
    echo ═══════════════════════════════════════════════════════════════
    echo.
    echo Ahora puedes:
    echo   1. Abrir VultrDriveDesktop.exe
    echo   2. Hacer clic en "Montar como unidad"
    echo   3. ¡Usar tu disco virtual!
    echo.
) else (
    echo ✗ ERROR: La instalación no se completó correctamente
    echo.
    echo SOLUCIÓN:
    echo   1. Cierra este script
    echo   2. Descarga manualmente: https://winfsp.dev/rel/
    echo   3. Instala: winfsp-2.0.23075.msi
    echo   4. Reinicia VultrDriveDesktop
    echo.
)

:: Limpiar archivos temporales
if exist "%TEMP_DIR%\winfsp.msi" del "%TEMP_DIR%\winfsp.msi"
if exist "%TEMP_DIR%" rmdir "%TEMP_DIR%"

echo.
pause
