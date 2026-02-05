# Verificacion de WinFsp y Rclone
Write-Host "=== Verificacion de Rclone y WinFsp ===" -ForegroundColor Cyan
Write-Host ""

# 1. Verificar rclone
Write-Host "1. Verificando rclone..." -ForegroundColor Yellow
$rclonePath = ".\rclone-v1.71.2-windows-amd64\rclone.exe"
if (Test-Path $rclonePath) {
    Write-Host "   OK - Rclone encontrado" -ForegroundColor Green
    & $rclonePath version | Select-Object -First 1
} else {
    Write-Host "   ERROR - Rclone no encontrado" -ForegroundColor Red
}

Write-Host ""
Write-Host "2. Verificando WinFsp..." -ForegroundColor Yellow
$winfspPath = "C:\Program Files (x86)\WinFsp"
if (Test-Path $winfspPath) {
    Write-Host "   OK - WinFsp instalado en: $winfspPath" -ForegroundColor Green
} else {
    Write-Host "   ERROR - WinFsp NO esta instalado" -ForegroundColor Red
    Write-Host ""
    Write-Host "   WinFsp es REQUERIDO para montar unidades en Windows" -ForegroundColor Yellow
    Write-Host "   Descarga: https://winfsp.dev/rel/" -ForegroundColor Cyan
    Write-Host "   Instala: winfsp-2.0.23075.msi" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "Presiona Enter para continuar..."
Read-Host
