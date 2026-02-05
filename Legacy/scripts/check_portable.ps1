# Verificador Simple de Componentes Portables
# VultrDrive Desktop

Write-Host ""
Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host "   VultrDrive Desktop - Verificador Portable" -ForegroundColor Cyan
Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host ""

$errors = 0

# Verificar app.py
if (Test-Path "app.py") {
    Write-Host "[OK] app.py encontrado" -ForegroundColor Green
} else {
    Write-Host "[ERROR] app.py NO encontrado" -ForegroundColor Red
    $errors++
}

# Verificar carpeta ui
if (Test-Path "ui\main_window.py") {
    Write-Host "[OK] Interfaz UI encontrada" -ForegroundColor Green
} else {
    Write-Host "[ERROR] ui\main_window.py NO encontrado" -ForegroundColor Red
    $errors++
}

# Verificar Rclone
$rcloneDirs = Get-ChildItem "." -Directory | Where-Object { $_.Name -like "rclone*" }
if ($rcloneDirs.Count -gt 0) {
    $rcloneExe = Get-ChildItem $rcloneDirs[0].FullName -Filter "rclone.exe" -ErrorAction SilentlyContinue
    if ($rcloneExe) {
        Write-Host "[OK] Rclone encontrado: $($rcloneDirs[0].Name)" -ForegroundColor Green
    } else {
        Write-Host "[ERROR] rclone.exe NO encontrado" -ForegroundColor Red
        $errors++
    }
} else {
    Write-Host "[ERROR] Carpeta rclone NO encontrada" -ForegroundColor Red
    $errors++
}

# Verificar instalador de WinFsp
Write-Host ""
Write-Host "Verificando instalador de WinFsp..." -ForegroundColor Yellow

if (-not (Test-Path "dependencies")) {
    New-Item -ItemType Directory -Path "dependencies" -Force | Out-Null
    Write-Host "[INFO] Carpeta dependencies creada" -ForegroundColor Yellow
}

$winfspMsi = Get-ChildItem "dependencies" -Filter "winfsp*.msi" -ErrorAction SilentlyContinue
if ($winfspMsi) {
    $sizeMB = [math]::Round($winfspMsi[0].Length / 1MB, 2)
    Write-Host "[OK] WinFsp MSI encontrado: $($winfspMsi[0].Name) ($sizeMB MB)" -ForegroundColor Green
} else {
    Write-Host "[ERROR] WinFsp MSI NO encontrado en dependencies\" -ForegroundColor Red
    $errors++
}

# Verificar si WinFsp ya esta instalado en el sistema
Write-Host ""
Write-Host "Verificando WinFsp en el sistema..." -ForegroundColor Yellow

$winfspInstalled = $false
$paths = @(
    "C:\Program Files (x86)\WinFsp\bin\winfsp-x64.dll",
    "C:\Program Files\WinFsp\bin\winfsp-x64.dll"
)

foreach ($path in $paths) {
    if (Test-Path $path) {
        Write-Host "[OK] WinFsp YA ESTA INSTALADO en el sistema" -ForegroundColor Green
        $winfspInstalled = $true
        break
    }
}

if (-not $winfspInstalled) {
    Write-Host "[INFO] WinFsp NO esta instalado (se instalara al ejecutar)" -ForegroundColor Yellow
}

# Resumen
Write-Host ""
Write-Host "=====================================================" -ForegroundColor Cyan

if ($errors -eq 0) {
    Write-Host " TODO LISTO - El programa es 100% portable" -ForegroundColor Green
    Write-Host ""
    Write-Host " Puedes copiar esta carpeta a cualquier PC Windows" -ForegroundColor Gray
    Write-Host " WinFsp se instalara automaticamente la primera vez" -ForegroundColor Gray
} else {
    Write-Host " ERRORES ENCONTRADOS: $errors" -ForegroundColor Red
    Write-Host ""
    Write-Host " Revisa los errores arriba antes de distribuir" -ForegroundColor Gray
}

Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host ""

