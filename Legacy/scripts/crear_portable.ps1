# Script para crear versión PORTABLE de VultrDriveDesktop
# Crea un ejecutable .exe con todo incluido (Python, PyQt6, boto3, etc.)

Write-Host "=== Creador de Version Portable - VultrDriveDesktop ===" -ForegroundColor Cyan
Write-Host ""

# Asegurarse de ejecutar dentro del directorio del script
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

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
    } catch {}
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
} else {
    Write-Host "   ERROR - No se pudo instalar PyInstaller" -ForegroundColor Red
    exit 1
}

# 3. Crear carpeta de distribución
Write-Host ""
Write-Host "3. Preparando carpeta de distribución..." -ForegroundColor Yellow
$distFolder = Join-Path $scriptDir "VultrDriveDesktop-Portable"

# Asegurarse de que no quede un proceso del portable en ejecución
$runningPortable = Get-Process -Name "VultrDriveDesktop" -ErrorAction SilentlyContinue
if ($runningPortable) {
    Write-Host "   Cerrando instancia previa de VultrDriveDesktop.exe" -ForegroundColor Gray
    $runningPortable | Stop-Process -Force -ErrorAction SilentlyContinue
    Start-Sleep -Milliseconds 500
}

if (Test-Path $distFolder) {
    Remove-Item $distFolder -Recurse -Force -ErrorAction SilentlyContinue
    if (Test-Path $distFolder) {
        # Reintentar con un breve retraso por si algún archivo sigue liberándose
        Start-Sleep -Milliseconds 500
        Remove-Item $distFolder -Recurse -Force -ErrorAction SilentlyContinue
    }
}
New-Item -ItemType Directory -Path $distFolder | Out-Null
Write-Host "   OK - Carpeta creada: $distFolder" -ForegroundColor Green

# 4. Compilar aplicación con PyInstaller
Write-Host ""
Write-Host "4. Compilando aplicación (esto puede tardar 2-5 minutos)..." -ForegroundColor Yellow
Write-Host "   Por favor espera..." -ForegroundColor Gray

$pyinstallerArgs = @(
    '--name=VultrDriveDesktop',
    '--onefile',
    '--windowed',
    '--icon=NONE',
    '--add-data=ui;ui',
    '--add-data=translations.py;.',
    '--add-data=theme_manager.py;.',
    '--add-data=config_manager.py;.',
    '--add-data=s3_handler.py;.',
    '--add-data=rclone_manager.py;.',
    '--add-data=file_watcher.py;.',
    '--add-data=drive_detector.py;.',
    '--add-data=splash_screen.py;.',
    '--hidden-import=PyQt6',
    '--hidden-import=boto3',
    '--hidden-import=botocore',
    '--hidden-import=watchdog',
    '--collect-all=PyQt6',
    '--collect-all=boto3',
    '--collect-all=botocore',
    '--collect-submodules=watchdog',
    '--collect-submodules=boto3',
    '--collect-submodules=botocore',
    '--noconsole',
    'app.py'
)

& $pythonCmd -m PyInstaller @pyinstallerArgs 2>&1 | Out-Null

if ($LASTEXITCODE -eq 0 -and (Test-Path ".\dist\VultrDriveDesktop.exe")) {
    Write-Host "   OK - Aplicacion compilada exitosamente" -ForegroundColor Green
} else {
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
} elseif (Test-Path ".\rclone.exe") {
    Copy-Item ".\rclone.exe" "$distFolder\" -Force
    Write-Host "   OK - Rclone copiado" -ForegroundColor Green
}

# 7. Copiar configuración y datos persistentes
Write-Host "   Copiando configuraciones y datos..." -ForegroundColor Gray
$configFiles = @(
    "config.json",
    "user_preferences.json",
    "config.default.json",
    "config.example.json"
)
foreach ($file in $configFiles) {
    if (Test-Path $file) {
        Copy-Item $file "$distFolder\" -Force
    }
}
Write-Host "   OK - Configuraciones copiadas" -ForegroundColor Green

# 8. Copiar scripts auxiliares (WinFsp y utilidades)
Write-Host "   Copiando scripts auxiliares..." -ForegroundColor Gray
$helperItems = @(
    "INSTALAR_WINFSP.bat",
    "instalar_winfsp.ps1",
    "verificar_winfsp.ps1",
    "run_app.ps1",
    "start.bat",
    "start.ps1"
)
foreach ($item in $helperItems) {
    if (Test-Path $item) {
        Copy-Item $item "$distFolder\" -Force
    }
}

# Incluir instalador WinFsp (descarga automática si no existe)
$winfspFileName = "winfsp-2.0.23075.msi"
$winfspLocalPath = Join-Path $scriptDir $winfspFileName
if (-not (Test-Path $winfspLocalPath)) {
    Write-Host "   Descargando WinFsp $winfspFileName..." -ForegroundColor Gray
    try {
        $progressPreferenceBackup = $global:ProgressPreference
        $global:ProgressPreference = 'SilentlyContinue'
        Invoke-WebRequest -Uri "https://github.com/winfsp/winfsp/releases/download/v2.0/$winfspFileName" -OutFile $winfspLocalPath -UseBasicParsing
    } catch {
        Write-Host "   ADVERTENCIA: No se pudo descargar WinFsp automáticamente." -ForegroundColor Yellow
    } finally {
        $global:ProgressPreference = $progressPreferenceBackup
    }
}
if (Test-Path $winfspLocalPath) {
    Copy-Item $winfspLocalPath "$distFolder\" -Force
    Write-Host "   OK - WinFsp incluido en la carpeta portable" -ForegroundColor Green
} else {
    Write-Host "   ⚠️  WinFsp no está incluido. El usuario necesitará conexión a internet." -ForegroundColor Yellow
}
Write-Host "   OK - Scripts auxiliares listos" -ForegroundColor Green

# 9. Copiar documentación
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

# 10. Crear README para versión portable
Write-Host "   Creando README portable..." -ForegroundColor Gray
$readmePortable = @"
# VultrDriveDesktop - Version Portable

- VultrDriveDesktop.exe (aplicacion completa con Python, PyQt6, boto3)
- rclone.exe (para montar unidades)
- config.json y user_preferences.json con tus credenciales y ajustes
- Scripts auxiliares (INSTALAR_WINFSP.bat, instalar_winfsp.ps1)
- Documentacion completa

## REQUISITO UNICO: WinFsp
Para montar unidades como disco, necesitas instalar WinFsp (solo una vez):
1. Descarga: https://winfsp.dev/rel/
2. Instala: winfsp-2.0.23075.msi

## Como usar:
1. Copia esta carpeta a la ubicacion que desees (USB, Escritorio, etc.)
2. Doble clic en VultrDriveDesktop.exe
3. Tus perfiles y preferencias se cargan automaticamente desde config.json
4. Listo!

## Ventajas de esta version:
- No necesita Python instalado
- No necesita pip install
- Todo en una carpeta
- Copia a USB y usa en cualquier PC
- Rapido y ligero

## Nota:
- La primera ejecucion puede tardar 5-10 segundos (descompresion)
- Los archivos de configuracion se guardan en la carpeta del programa
- Puedes editar config.json para agregar o cambiar perfiles sin reinstalar

Fecha de compilacion: $(Get-Date -Format "dd/MM/yyyy HH:mm")
Version: 2.0 Portable
"@
Set-Content -Path "$distFolder\README.txt" -Value $readmePortable -Encoding UTF8
Write-Host "   OK - README creado" -ForegroundColor Green

# 11. Crear script de inicio rapido
$startScript = @"
@echo off
echo Iniciando VultrDriveDesktop Portable...
start VultrDriveDesktop.exe
"@
Set-Content -Path "$distFolder\Iniciar.bat" -Value $startScript -Encoding ASCII
Write-Host "   OK - Script de inicio creado" -ForegroundColor Green

# 12. Limpiar archivos temporales
Write-Host ""
Write-Host "6. Limpiando archivos temporales..." -ForegroundColor Yellow
Remove-Item ".\build" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item ".\dist" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item ".\VultrDriveDesktop.spec" -Force -ErrorAction SilentlyContinue
Write-Host "   OK - Limpieza completada" -ForegroundColor Green

# 13. Calcular tamaño
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
Write-Host "  [✓] Todo autocontenido" -ForegroundColor Green
Write-Host "  [✓] Portable - Lleva a cualquier PC" -ForegroundColor Green
Write-Host "  [✓] Sin perdida de funciones" -ForegroundColor Green
Write-Host "  [✓] Mismo rendimiento" -ForegroundColor Green
Write-Host ""
Write-Host "Presiona Enter para continuar..."
Read-Host
