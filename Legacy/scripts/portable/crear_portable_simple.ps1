# Crear version PORTABLE de VultrDrive Desktop

$timestamp = Get-Date -Format "yyyyMMdd_HHmm"
$sourcePath = Split-Path -Parent $MyInvocation.MyCommand.Path
$portablePath = Join-Path (Split-Path -Parent $sourcePath) "VultrDrive_Portable_$timestamp"

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host " Creando VultrDrive Desktop PORTABLE" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Crear carpeta portable
Write-Host "[1/5] Creando carpeta..." -ForegroundColor Yellow
New-Item -ItemType Directory -Path $portablePath -Force | Out-Null
Write-Host "  OK: $portablePath" -ForegroundColor Green
Write-Host ""

# Copiar archivos Python esenciales
Write-Host "[2/5] Copiando archivos principales..." -ForegroundColor Yellow
$mainFiles = @(
    "app.py",
    "config_manager.py",
    "rclone_manager.py",
    "theme_manager.py",
    "translations.py",
    "translations_base.py",
    "splash_screen.py",
    "s3_handler.py",
    "drive_detector.py",
    "file_watcher.py",
    "ejecutar_app.bat",
    "requirements.txt",
    "LICENSE",
    "config.default.json",
    "config.example.json"
)

foreach ($file in $mainFiles) {
    $srcFile = Join-Path $sourcePath $file
    if (Test-Path $srcFile) {
        Copy-Item $srcFile $portablePath -Force
        Write-Host "  OK: $file" -ForegroundColor Green
    }
}

# Copiar config.json si existe
if (Test-Path (Join-Path $sourcePath "config.json")) {
    Copy-Item (Join-Path $sourcePath "config.json") $portablePath -Force
    Write-Host "  OK: config.json" -ForegroundColor Green
}
Write-Host ""

# Copiar carpetas
Write-Host "[3/5] Copiando carpetas..." -ForegroundColor Yellow

# UI
if (Test-Path (Join-Path $sourcePath "ui")) {
    Copy-Item (Join-Path $sourcePath "ui") $portablePath -Recurse -Force
    Write-Host "  OK: ui\" -ForegroundColor Green
}

# Dependencies
if (Test-Path (Join-Path $sourcePath "dependencies")) {
    Copy-Item (Join-Path $sourcePath "dependencies") $portablePath -Recurse -Force
    Write-Host "  OK: dependencies\" -ForegroundColor Green
}

# Rclone
$rcloneDirs = Get-ChildItem $sourcePath -Directory | Where-Object { $_.Name -like "rclone*" }
if ($rcloneDirs.Count -gt 0) {
    Copy-Item $rcloneDirs[0].FullName $portablePath -Recurse -Force
    Write-Host "  OK: $($rcloneDirs[0].Name)\" -ForegroundColor Green
}
Write-Host ""

# Crear README simple
Write-Host "[4/5] Creando documentacion..." -ForegroundColor Yellow

$readme = "VultrDrive Desktop - Version Portable`n`n"
$readme += "INICIO RAPIDO`n"
$readme += "=============`n`n"
$readme += "1. Ejecuta: ejecutar_app.bat`n"
$readme += "2. Si aparece UAC, haz clic en SI`n"
$readme += "3. WinFsp se instala automaticamente (solo primera vez)`n"
$readme += "4. Listo para usar`n`n"
$readme += "REQUISITOS`n"
$readme += "==========`n`n"
$readme += "- Windows 10/11 (64-bit)`n"
$readme += "- Permisos de administrador (solo para instalar WinFsp)`n`n"
$readme += "PORTABLE`n"
$readme += "========`n`n"
$readme += "- Funciona desde cualquier ubicacion`n"
$readme += "- USB, Escritorio, Documentos, etc.`n"
$readme += "- No necesita instalacion previa`n"
$readme += "- WinFsp se instala automaticamente`n"
$readme += "- Incluye todo lo necesario`n`n"
$readme += "Version creada: $(Get-Date -Format 'dd/MM/yyyy HH:mm')`n"

$readme | Out-File (Join-Path $portablePath "README.txt") -Encoding UTF8
Write-Host "  OK: README.txt" -ForegroundColor Green

# Copiar LEEME si existe
if (Test-Path (Join-Path $sourcePath "LEEME_PRIMERO.txt")) {
    Copy-Item (Join-Path $sourcePath "LEEME_PRIMERO.txt") $portablePath -Force
    Write-Host "  OK: LEEME_PRIMERO.txt" -ForegroundColor Green
}
Write-Host ""

# Verificar
Write-Host "[5/5] Verificando..." -ForegroundColor Yellow
$ok = $true

if (-not (Test-Path (Join-Path $portablePath "app.py"))) { $ok = $false }
if (-not (Test-Path (Join-Path $portablePath "ejecutar_app.bat"))) { $ok = $false }
if (-not (Test-Path (Join-Path $portablePath "ui\main_window.py"))) { $ok = $false }

$winfsp = Get-ChildItem (Join-Path $portablePath "dependencies") -Filter "winfsp*.msi" -ErrorAction SilentlyContinue
if (-not $winfsp) { $ok = $false }

$rclone = Get-ChildItem $portablePath -Recurse -Filter "rclone.exe" -ErrorAction SilentlyContinue
if (-not $rclone) { $ok = $false }

if ($ok) {
    Write-Host "  OK: Todos los componentes presentes" -ForegroundColor Green
} else {
    Write-Host "  ERROR: Faltan componentes" -ForegroundColor Red
}
Write-Host ""

# Estadisticas
$totalSize = (Get-ChildItem $portablePath -Recurse -File | Measure-Object -Property Length -Sum).Sum / 1MB
$fileCount = (Get-ChildItem $portablePath -Recurse -File).Count

Write-Host "============================================" -ForegroundColor Cyan
Write-Host " VERSION PORTABLE CREADA" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Ubicacion: $portablePath" -ForegroundColor White
Write-Host "Tamano: $([math]::Round($totalSize, 2)) MB" -ForegroundColor White
Write-Host "Archivos: $fileCount" -ForegroundColor White
Write-Host ""

if ($ok) {
    Write-Host "LISTO - Version portable completa" -ForegroundColor Green
    Write-Host ""
    Write-Host "Puedes copiar esta carpeta a cualquier PC Windows" -ForegroundColor Gray
    Write-Host "y ejecutar: ejecutar_app.bat" -ForegroundColor Gray
} else {
    Write-Host "ADVERTENCIA - Revisa los componentes" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Abrir explorador
Start-Process explorer.exe -ArgumentList $portablePath

