# Instalador automatico de WinFsp
Write-Host "=== Instalador de WinFsp para Windows ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "WinFsp es requerido para montar almacenamiento como unidades en Windows." -ForegroundColor Yellow
Write-Host ""

# URL de descarga de WinFsp
$winfspUrl = "https://github.com/winfsp/winfsp/releases/download/v2.0/winfsp-2.0.23075.msi"
$winfspInstaller = "$env:TEMP\winfsp-installer.msi"

Write-Host "1. Descargando WinFsp..." -ForegroundColor Yellow
try {
    Invoke-WebRequest -Uri $winfspUrl -OutFile $winfspInstaller -UseBasicParsing
    Write-Host "   OK - Descargado" -ForegroundColor Green
} catch {
    Write-Host "   ERROR - No se pudo descargar" -ForegroundColor Red
    Write-Host "   Por favor descarga manualmente desde: $winfspUrl" -ForegroundColor Cyan
    exit 1
}

Write-Host ""
Write-Host "2. Instalando WinFsp..." -ForegroundColor Yellow
Write-Host "   (Se abrira el instalador de Windows)" -ForegroundColor Gray
Write-Host ""

# Ejecutar instalador MSI
Start-Process msiexec.exe -ArgumentList "/i `"$winfspInstaller`" /qb" -Wait -Verb RunAs

# Verificar instalacion
Write-Host ""
Write-Host "3. Verificando instalacion..." -ForegroundColor Yellow
$winfspPath = "C:\Program Files (x86)\WinFsp"
if (Test-Path $winfspPath) {
    Write-Host "   OK - WinFsp instalado correctamente" -ForegroundColor Green
    Write-Host ""
    Write-Host "Ahora puedes montar unidades en VultrDriveDesktop" -ForegroundColor Green
} else {
    Write-Host "   ERROR - La instalacion pudo haber fallado" -ForegroundColor Red
    Write-Host "   Intenta instalar manualmente desde: $winfspUrl" -ForegroundColor Cyan
}

# Limpiar
Remove-Item $winfspInstaller -ErrorAction SilentlyContinue

Write-Host ""
Write-Host "Presiona Enter para continuar..."
Read-Host
