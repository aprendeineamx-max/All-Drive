# Script para crear versión PORTABLE de VultrDriveDesktop
# Crea un ejecutable .exe con todo incluido (Python, PyQt6, boto3, etc.)

Write-Host "=== Creador de Version Portable - VultrDriveDesktop ===" -ForegroundColor Cyan
Write-Host ""

# 1. Verificar Python
Write-Host "1. Verificando Python..." -ForegroundColor Yellow
$pythonCmd = $null
foreach ($cmd in @("py", "python", "python3")) {
    try {
        $version = & $cmd --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            $pythonCmd = $cmd
            Write-Host "   OK - Python encontrado: $version" -ForegroundColor Green
            break
        }
    }
    catch {}
}

if (-not $pythonCmd) {
    Write-Host "   ERROR - Python no encontrado" -ForegroundColor Red
    exit 1
}

# 2. Instalar PyInstaller
Write-Host ""
Write-Host "2. Instalando PyInstaller..." -ForegroundColor Yellow
& $pythonCmd -m pip install pyinstaller --quiet --disable-pip-version-check
if ($LASTEXITCODE -eq 0) {
    Write-Host "   OK - PyInstaller instalado" -ForegroundColor Green
}
else {
    Write-Host "   ERROR - No se pudo instalar PyInstaller" -ForegroundColor Red
    exit 1
}

# 3. Crear carpeta de distribución
Write-Host ""
Write-Host "3. Preparando carpeta de distribución..." -ForegroundColor Yellow
$distFolder = ".\VultrDriveDesktop-Portable"
if (Test-Path $distFolder) {
    Remove-Item $distFolder -Recurse -Force
}
New-Item -ItemType Directory -Path $distFolder | Out-Null
Write-Host "   OK - Carpeta creada: $distFolder" -ForegroundColor Green

# 4. Compilar aplicación con PyInstaller
Write-Host ""
Write-Host "4. Compilando aplicación (esto puede tardar 2-5 minutos)..." -ForegroundColor Yellow
Write-Host "   Por favor espera..." -ForegroundColor Gray

$pyinstallerArgs = @(
    "--name=VultrDriveDesktop",
    "--onefile",
    "--windowed",
    "--icon=NONE",
    "--add-data=ui;ui",
    "--add-data=translations.py;.",
    "--add-data=theme_manager.py;.",
    "--add-data=splash_screen.py;.",
    "--add-data=config_manager.py;.",
    "--add-data=s3_handler.py;.",
    "--add-data=rclone_manager.py;.",
    "--add-data=file_watcher.py;.",
    "--hidden-import=PyQt6",
    "--hidden-import=boto3",
    "--hidden-import=botocore",
    "--hidden-import=watchdog",
    "--hidden-import=google.cloud.storage",
    "--hidden-import=google.auth",
    "--hidden-import=google.api_core",
    "--hidden-import=azure.identity",
    "--hidden-import=azure.storage.blob",
    "--hidden-import=azure.mgmt.compute",
    "--hidden-import=azure.mgmt.resource",
    "--collect-all=PyQt6",
    "--collect-all=boto3",
    "--collect-all=botocore",
    "--collect-all=google.cloud.storage",
    "--noconsole",
    "app.py"
)

& $pythonCmd -m PyInstaller @pyinstallerArgs 2>&1 | Out-Null

if ($LASTEXITCODE -eq 0 -and (Test-Path ".\dist\VultrDriveDesktop.exe")) {
    Write-Host "   OK - Aplicacion compilada exitosamente" -ForegroundColor Green
}
else {
    Write-Host "   ERROR - La compilacion fallo" -ForegroundColor Red
    Write-Host "   Revisa los logs en build/ para mas detalles" -ForegroundColor Yellow
    exit 1
}

# 5. Copiar ejecutable
Write-Host ""
Write-Host "5. Copiando archivos..." -ForegroundColor Yellow
Copy-Item ".\dist\VultrDriveDesktop.exe" "$distFolder\" -Force
Write-Host "   OK - Ejecutable copiado" -ForegroundColor Green

# 6. Copiar Rclone
if (Test-Path ".\rclone-v1.71.2-windows-amd64\rclone.exe") {
    Copy-Item ".\rclone-v1.71.2-windows-amd64\rclone.exe" "$distFolder\" -Force
    Write-Host "   OK - Rclone copiado" -ForegroundColor Green
}
elseif (Test-Path ".\rclone.exe") {
    Copy-Item ".\rclone.exe" "$distFolder\" -Force
    Write-Host "   OK - Rclone copiado" -ForegroundColor Green
}

# 6.5. Copiar configuracion predeterminada (NUEVO)
Write-Host "   Copiando configuracion predeterminada..." -ForegroundColor Gray
if (Test-Path ".\config.default.json") {
    Copy-Item ".\config.default.json" "$distFolder\config.json" -Force
    Write-Host "   OK - Configuracion predeterminada incluida" -ForegroundColor Green
}
elseif (Test-Path ".\config.json") {
    Copy-Item ".\config.json" "$distFolder\config.json" -Force
    Write-Host "   OK - Configuracion actual incluida" -ForegroundColor Green
}

# 6.6. Copiar preferencias de usuario
if (Test-Path ".\user_preferences.json") {
    Copy-Item ".\user_preferences.json" "$distFolder\" -Force
    Write-Host "   OK - Preferencias de usuario incluidas" -ForegroundColor Green
}

# 6.7. Copiar credenciales de GCP (Claves GCP/)
Write-Host "   Copiando credenciales de GCP..." -ForegroundColor Gray
if (Test-Path ".\Claves GCP") {
    Copy-Item ".\Claves GCP" "$distFolder\Claves GCP" -Recurse -Force
    Write-Host "   OK - Credenciales de GCP incluidas" -ForegroundColor Green
}
else {
    Write-Host "   NOTA - No se encontraron credenciales GCP" -ForegroundColor Yellow
}

# 6.8. Copiar credenciales de Azure
Write-Host "   Copiando credenciales de Azure..." -ForegroundColor Gray
if (Test-Path ".\azure_creds.json") {
    Copy-Item ".\azure_creds.json" "$distFolder\" -Force
    Write-Host "   OK - azure_creds.json incluido" -ForegroundColor Green
}
if (Test-Path ".\azure_profiles.json") {
    Copy-Item ".\azure_profiles.json" "$distFolder\" -Force
    Write-Host "   OK - azure_profiles.json incluido" -ForegroundColor Green
}

# 6.9. Copiar credenciales de Vultr S3
Write-Host "   Copiando credenciales de Vultr..." -ForegroundColor Gray
if (Test-Path ".\vultr_creds.json") {
    Copy-Item ".\vultr_creds.json" "$distFolder\" -Force
    Write-Host "   OK - vultr_creds.json incluido" -ForegroundColor Green
}

# 6.10. Copiar configuración de Rclone
Write-Host "   Copiando configuración de Rclone..." -ForegroundColor Gray
if (Test-Path ".\rclone.conf") {
    Copy-Item ".\rclone.conf" "$distFolder\" -Force
    Write-Host "   OK - rclone.conf incluido" -ForegroundColor Green
}

# 6.11. Copiar Transfer Manager state (para resume de descargas)
Write-Host "   Copiando estado de transferencias..." -ForegroundColor Gray
if (Test-Path ".\active_transfers.json") {
    Copy-Item ".\active_transfers.json" "$distFolder\" -Force
    Write-Host "   OK - active_transfers.json incluido (para reanudar descargas)" -ForegroundColor Green
}

# 7. Copiar documentación
Write-Host "   Copiando documentacion..." -ForegroundColor Gray
$docFiles = @(
    "README_COMPLETO.md",
    "GUIA_VISUAL.md",
    "QUICK_START.md",
    "SOLUCION_MONTAJE.md"
)
foreach ($file in $docFiles) {
    if (Test-Path $file) {
        Copy-Item $file "$distFolder\" -Force
    }
}
Write-Host "   OK - Documentacion copiada" -ForegroundColor Green

# 7.5. Copiar instalador de WinFsp
Write-Host "   Copiando instalador de WinFsp..." -ForegroundColor Gray
if (Test-Path ".\INSTALAR_WINFSP.bat") {
    Copy-Item ".\INSTALAR_WINFSP.bat" "$distFolder\" -Force
    Write-Host "   OK - Instalador de WinFsp incluido" -ForegroundColor Green
}

# 8. Crear README para versión portable
Write-Host "   Creando README portable..." -ForegroundColor Gray
$readmePortable = @"
# VultrDriveDesktop - Version Portable v2.0

## Que incluye esta version:
- VultrDriveDesktop.exe (aplicacion completa con Python, PyQt6, boto3)
- rclone.exe (para montar unidades)
- config.json (TU CONFIGURACION PREDETERMINADA INCLUIDA)
- user_preferences.json (tus preferencias de idioma/tema)
- Documentacion completa

## CONFIGURACION PREINSTALADA:
Tu perfil "almacen-de-backups-cuenta-destino" esta preconfigurado.
Al abrir la aplicacion, tu cuenta ya esta lista para usar.
Solo selecciona tu perfil del dropdown y empieza a trabajar.

## REQUISITO UNICO: WinFsp (OPCIONAL)
Para montar unidades como disco, necesitas instalar WinFsp (solo una vez):
1. Descarga: https://winfsp.dev/rel/
2. Instala: winfsp-2.0.23075.msi

## Como usar:
1. Doble clic en VultrDriveDesktop.exe
2. Tu perfil ya esta configurado
3. Selecciona "almacen-de-backups-cuenta-destino" del dropdown
4. ¡Listo para usar!

## Ventajas de esta version:
- No necesita Python instalado
- No necesita pip install
- Todo en una carpeta
- Copia a USB y usa en cualquier PC
- TU CONFIGURACION YA INCLUIDA
- Listo para usar inmediatamente

## Nota:
- La primera ejecucion puede tardar 5-10 segundos (descompresion)
- Los archivos de configuracion viajan contigo en esta carpeta

Fecha de compilacion: $(Get-Date -Format "dd/MM/yyyy HH:mm")
Version: 2.0 Portable con Configuracion Incluida
"@
Set-Content -Path "$distFolder\README.txt" -Value $readmePortable -Encoding UTF8
Write-Host "   OK - README creado" -ForegroundColor Green

# 9. Crear script de inicio rapido
$startScript = @"
@echo off
echo Iniciando VultrDriveDesktop Portable...
start VultrDriveDesktop.exe
"@
Set-Content -Path "$distFolder\Iniciar.bat" -Value $startScript -Encoding ASCII
Write-Host "   OK - Script de inicio creado" -ForegroundColor Green

# 10. Limpiar archivos temporales
Write-Host ""
Write-Host "6. Limpiando archivos temporales..." -ForegroundColor Yellow
Remove-Item ".\build" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item ".\dist" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item ".\VultrDriveDesktop.spec" -Force -ErrorAction SilentlyContinue
Write-Host "   OK - Limpieza completada" -ForegroundColor Green

# 11. Calcular tamaño
Write-Host ""
Write-Host "7. Informacion final..." -ForegroundColor Yellow
$totalSize = (Get-ChildItem $distFolder -Recurse | Measure-Object -Property Length -Sum).Sum
$sizeMB = [math]::Round($totalSize / 1MB, 2)
Write-Host "   Tamano total: $sizeMB MB" -ForegroundColor Cyan

# Resumen
Write-Host ""
Write-Host "=== COMPILACION EXITOSA ===" -ForegroundColor Green
Write-Host ""
Write-Host "Version portable creada en: $distFolder" -ForegroundColor Cyan
Write-Host ""
Write-Host "Contenido:" -ForegroundColor Yellow
Get-ChildItem $distFolder | ForEach-Object {
    Write-Host "  - $($_.Name)" -ForegroundColor White
}
Write-Host ""
Write-Host "Para distribuir:" -ForegroundColor Yellow
Write-Host "1. Comprime la carpeta $distFolder en .zip" -ForegroundColor White
Write-Host "2. Copia a USB o compartela" -ForegroundColor White
Write-Host "3. En la otra PC:" -ForegroundColor White
Write-Host "   - Descomprime" -ForegroundColor White
Write-Host "   - Instala WinFsp (solo si quieres montar unidades)" -ForegroundColor White
Write-Host "   - Doble clic en VultrDriveDesktop.exe" -ForegroundColor White
Write-Host ""
Write-Host "VENTAJAS:" -ForegroundColor Green
Write-Host "  [✓] No necesita Python instalado" -ForegroundColor Green
Write-Host "  [✓] No necesita pip install" -ForegroundColor Green
Write-Host "  [✓] Tu configuracion YA INCLUIDA" -ForegroundColor Green
Write-Host "  [✓] Todo autocontenido" -ForegroundColor Green
Write-Host "  [✓] Portable - Lleva a cualquier PC" -ForegroundColor Green
Write-Host "  [✓] Sin perdida de funciones" -ForegroundColor Green
Write-Host "  [✓] Mismo rendimiento" -ForegroundColor Green
Write-Host "  [✓] Listo para usar inmediatamente" -ForegroundColor Green
Write-Host ""
Write-Host "Presiona Enter para continuar..."
Read-Host
