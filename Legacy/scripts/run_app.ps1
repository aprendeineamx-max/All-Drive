# Startup script para VultrDriveDesktop con mejoras
# Actualizado: 06/11/2025

Write-Host "=== Iniciando VultrDriveDesktop con mejoras ===" -ForegroundColor Cyan
Write-Host ""

# Verificar si Python está instalado
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Python encontrado: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Python no encontrado. Por favor instale Python primero." -ForegroundColor Red
    exit 1
}

# Verificar si los archivos necesarios existen
$requiredFiles = @(
    "app.py",
    "translations.py", 
    "theme_manager.py",
    "ui\main_window.py",
    "config_manager.py",
    "s3_handler.py",
    "rclone_manager.py"
)

$missingFiles = @()
foreach ($file in $requiredFiles) {
    if (-not (Test-Path $file)) {
        $missingFiles += $file
    }
}

if ($missingFiles.Count -gt 0) {
    Write-Host "✗ Archivos faltantes:" -ForegroundColor Red
    foreach ($file in $missingFiles) {
        Write-Host "  - $file" -ForegroundColor Red
    }
    exit 1
}

Write-Host "✓ Todos los archivos necesarios encontrados" -ForegroundColor Green

# Verificar e instalar dependencias
Write-Host ""
Write-Host "Verificando dependencias de Python..." -ForegroundColor Yellow

$dependencies = @("PyQt6", "boto3", "watchdog")
$missingDeps = @()

foreach ($dep in $dependencies) {
    try {
        $importName = $dep.ToLower().Replace('pyqt6', 'PyQt6')
        python -c "import $importName" 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ $dep instalado" -ForegroundColor Green
        } else {
            $missingDeps += $dep
        }
    } catch {
        $missingDeps += $dep
    }
}

if ($missingDeps.Count -gt 0) {
    Write-Host ""
    Write-Host "Instalando dependencias faltantes..." -ForegroundColor Yellow
    foreach ($dep in $missingDeps) {
        Write-Host "Instalando $dep..." -ForegroundColor Yellow
        pip install $dep
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ $dep instalado correctamente" -ForegroundColor Green
        } else {
            Write-Host "✗ Error instalando $dep" -ForegroundColor Red
        }
    }
}

# Verificar rclone
Write-Host ""
Write-Host "Verificando rclone..." -ForegroundColor Yellow
$rclonePaths = @(
    "rclone.exe",
    "rclone-v1.71.2-windows-amd64\rclone.exe"
)

$rcloneFound = $false
foreach ($path in $rclonePaths) {
    if (Test-Path $path) {
        Write-Host "✓ rclone encontrado en: $path" -ForegroundColor Green
        $rcloneFound = $true
        break
    }
}

if (-not $rcloneFound) {
    Write-Host "⚠ rclone no encontrado. La función de montaje puede no funcionar." -ForegroundColor Yellow
    Write-Host "  Descarga rclone desde: https://rclone.org/downloads/" -ForegroundColor Gray
}

Write-Host ""
Write-Host "=== Iniciando aplicación ===" -ForegroundColor Cyan
Write-Host ""

# Verificar si hay preferencias guardadas
if (Test-Path "user_preferences.json") {
    try {
        $prefs = Get-Content "user_preferences.json" | ConvertFrom-Json
        Write-Host "✓ Preferencias de usuario cargadas:" -ForegroundColor Green
        Write-Host "  - Idioma: $($prefs.language)" -ForegroundColor Gray
        Write-Host "  - Tema: $($prefs.theme)" -ForegroundColor Gray
    } catch {
        Write-Host "⚠ Error leyendo preferencias de usuario" -ForegroundColor Yellow
    }
} else {
    Write-Host "ℹ Primera ejecución - se usarán valores por defecto" -ForegroundColor Cyan
    Write-Host "  - Idioma: Inglés (EN)" -ForegroundColor Gray
    Write-Host "  - Tema: Oscuro" -ForegroundColor Gray
}

Write-Host ""
Write-Host "Lanzando VultrDriveDesktop..." -ForegroundColor Green
Write-Host ""

# Ejecutar la aplicación
try {
    python app.py
} catch {
    Write-Host "✗ Error ejecutando la aplicación: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Presiona cualquier tecla para salir..." -ForegroundColor Gray
    $null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
}