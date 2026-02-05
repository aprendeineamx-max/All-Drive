# Script para crear una distribucion portable de VultrDrive Desktop
# Este script empaqueta todo lo necesario en una carpeta lista para distribuir

Write-Host ""
Write-Host "=========================================================" -ForegroundColor Cyan
Write-Host "  Creador de Distribucion Portable - VultrDrive Desktop" -ForegroundColor Cyan
Write-Host "=========================================================" -ForegroundColor Cyan
Write-Host ""

$sourceDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$portableDir = Join-Path $sourceDir "VultrDrive_Portable_$timestamp"

Write-Host "[1/6] Creando carpeta portable..." -ForegroundColor Yellow
New-Item -ItemType Directory -Path $portableDir -Force | Out-Null
Write-Host "      Carpeta creada: $portableDir" -ForegroundColor Gray

Write-Host ""
Write-Host "[2/6] Copiando archivos principales..." -ForegroundColor Yellow
$mainFiles = @(
    "app.py",
    "ejecutar_app.bat",
    "config.json",
    "config_manager.py",
    "rclone_manager.py",
    "theme_manager.py",
    "translations.py",
    "splash_screen.py",
    "requirements.txt",
    "LICENSE"
)

foreach ($file in $mainFiles) {
    if (Test-Path (Join-Path $sourceDir $file)) {
        Copy-Item (Join-Path $sourceDir $file) $portableDir -Force
        Write-Host "      [OK] $file" -ForegroundColor Green
    } else {
        Write-Host "      [SKIP] $file (no existe)" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "[3/6] Copiando carpetas..." -ForegroundColor Yellow

# Copiar carpeta ui
if (Test-Path (Join-Path $sourceDir "ui")) {
    Copy-Item (Join-Path $sourceDir "ui") $portableDir -Recurse -Force
    Write-Host "      [OK] ui\" -ForegroundColor Green
}

# Copiar carpeta de rclone
$rcloneDirs = Get-ChildItem $sourceDir -Directory | Where-Object { $_.Name -like "rclone*" }
if ($rcloneDirs.Count -gt 0) {
    Copy-Item $rcloneDirs[0].FullName $portableDir -Recurse -Force
    Write-Host "      [OK] $($rcloneDirs[0].Name)\" -ForegroundColor Green
}

Write-Host ""
Write-Host "[4/6] Copiando instalador de WinFsp..." -ForegroundColor Yellow

# Crear carpeta dependencies
$depDir = Join-Path $portableDir "dependencies"
New-Item -ItemType Directory -Path $depDir -Force | Out-Null

# Copiar WinFsp MSI
$winfspSource = Join-Path $sourceDir "dependencies\winfsp-2.0.23075.msi"
if (Test-Path $winfspSource) {
    Copy-Item $winfspSource $depDir -Force
    $sizeMB = [math]::Round((Get-Item $winfspSource).Length / 1MB, 2)
    Write-Host "      [OK] winfsp-2.0.23075.msi ($sizeMB MB)" -ForegroundColor Green
} else {
    Write-Host "      [ERROR] WinFsp MSI NO encontrado" -ForegroundColor Red
    Write-Host "      Descargando desde internet..." -ForegroundColor Yellow
    
    try {
        $winfspUrl = "https://github.com/winfsp/winfsp/releases/download/v2.0/winfsp-2.0.23075.msi"
        $winfspDest = Join-Path $depDir "winfsp-2.0.23075.msi"
        [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
        $ProgressPreference = 'SilentlyContinue'
        Invoke-WebRequest -Uri $winfspUrl -OutFile $winfspDest
        
        if (Test-Path $winfspDest) {
            $sizeMB = [math]::Round((Get-Item $winfspDest).Length / 1MB, 2)
            Write-Host "      [OK] Descargado exitosamente ($sizeMB MB)" -ForegroundColor Green
        }
    } catch {
        Write-Host "      [ERROR] No se pudo descargar: $_" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "[5/6] Creando documentacion..." -ForegroundColor Yellow

# Crear README portable
$readmeContent = @"
# VultrDrive Desktop - Version Portable

## Inicio Rapido

1. Ejecuta: ejecutar_app.bat
2. Si aparece UAC (Control de Cuentas), haz clic en "Si"
3. WinFsp se instalara automaticamente la primera vez
4. Listo para usar!

## Requisitos

- Windows 10/11 (64-bit)
- Permisos de administrador (solo para instalar WinFsp)

## Como Funciona

Este programa es 100% portable:
- No necesita instalacion
- Incluye todos los componentes necesarios
- WinFsp se instala automaticamente al primer uso
- Funciona desde cualquier ubicacion (USB, Escritorio, etc.)

## Soporte

- Documentacion completa: INSTALACION_AUTOMATICA_WINFSP.md
- Sitio web: https://vultr.com
- WinFsp info: https://winfsp.dev

## Licencia

Ver archivo LICENSE

---
Version portable creada: $(Get-Date -Format "dd/MM/yyyy HH:mm")
"@

$readmeContent | Out-File (Join-Path $portableDir "README_PORTABLE.txt") -Encoding UTF8
Write-Host "      [OK] README_PORTABLE.txt" -ForegroundColor Green

# Copiar documentacion adicional
$docs = @(
    "INSTALACION_AUTOMATICA_WINFSP.md",
    "README.md"
)

foreach ($doc in $docs) {
    if (Test-Path (Join-Path $sourceDir $doc)) {
        Copy-Item (Join-Path $sourceDir $doc) $portableDir -Force
        Write-Host "      [OK] $doc" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "[6/6] Verificando empaquetado..." -ForegroundColor Yellow

$errors = 0

# Verificar archivos criticos
if (-not (Test-Path (Join-Path $portableDir "app.py"))) { $errors++ }
if (-not (Test-Path (Join-Path $portableDir "ui\main_window.py"))) { $errors++ }
if (-not (Test-Path (Join-Path $portableDir "dependencies\winfsp-2.0.23075.msi"))) { $errors++ }

$rcloneExe = Get-ChildItem $portableDir -Recurse -Filter "rclone.exe" -ErrorAction SilentlyContinue
if (-not $rcloneExe) { $errors++ }

if ($errors -eq 0) {
    Write-Host "      [OK] Todos los componentes verificados" -ForegroundColor Green
} else {
    Write-Host "      [ERROR] Faltan $errors componentes criticos" -ForegroundColor Red
}

# Calcular tamano total
$totalSize = (Get-ChildItem $portableDir -Recurse | Measure-Object -Property Length -Sum).Sum / 1MB
$fileCount = (Get-ChildItem $portableDir -Recurse -File).Count

Write-Host ""
Write-Host "=========================================================" -ForegroundColor Cyan
Write-Host "                    DISTRIBUCION CREADA" -ForegroundColor Cyan
Write-Host "=========================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Ubicacion: $portableDir" -ForegroundColor White
Write-Host "  Tamano total: $([math]::Round($totalSize, 2)) MB" -ForegroundColor White
Write-Host "  Archivos: $fileCount" -ForegroundColor White
Write-Host ""

if ($errors -eq 0) {
    Write-Host "  [LISTO] La distribucion esta completa y lista para usar" -ForegroundColor Green
    Write-Host ""
    Write-Host "  Puedes copiar esta carpeta a:" -ForegroundColor Gray
    Write-Host "    - Otro PC Windows" -ForegroundColor Gray
    Write-Host "    - Una memoria USB" -ForegroundColor Gray
    Write-Host "    - Un servidor de archivos compartido" -ForegroundColor Gray
    Write-Host ""
    Write-Host "  El programa funcionara sin instalacion previa" -ForegroundColor Gray
    Write-Host "  WinFsp se instalara automaticamente al ejecutar" -ForegroundColor Gray
} else {
    Write-Host "  [ERROR] La distribucion tiene problemas" -ForegroundColor Red
    Write-Host "  Revisa los errores arriba" -ForegroundColor Gray
}

Write-Host ""
Write-Host "=========================================================" -ForegroundColor Cyan
Write-Host ""

