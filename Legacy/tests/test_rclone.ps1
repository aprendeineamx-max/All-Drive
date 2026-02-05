# Script para probar rclone y verificar WinFsp
Write-Host "=== Verificación de Rclone y WinFsp ===" -ForegroundColor Cyan
Write-Host ""

# 1. Verificar rclone
Write-Host "1. Verificando rclone..." -ForegroundColor Yellow
$rclonePaths = @(
    ".\rclone.exe",
    ".\rclone-v1.71.2-windows-amd64\rclone.exe"
)

$rcloneFound = $null
foreach ($path in $rclonePaths) {
    if (Test-Path $path) {
        $rcloneFound = $path
        Write-Host "   ✓ Rclone encontrado: $path" -ForegroundColor Green
        break
    }
}

if (-not $rcloneFound) {
    Write-Host "   ✗ Rclone no encontrado" -ForegroundColor Red
    exit 1
}

# 2. Verificar versión de rclone
Write-Host ""
Write-Host "2. Versión de rclone:" -ForegroundColor Yellow
& $rcloneFound version

# 3. Verificar WinFsp
Write-Host ""
Write-Host "3. Verificando WinFsp..." -ForegroundColor Yellow
$winfspPaths = @(
    "C:\Program Files (x86)\WinFsp",
    "C:\Program Files\WinFsp"
)

$winfspFound = $false
foreach ($path in $winfspPaths) {
    if (Test-Path $path) {
        $winfspFound = $true
        Write-Host "   ✓ WinFsp instalado en: $path" -ForegroundColor Green
        
        # Verificar driver
        $driver = Get-WmiObject Win32_SystemDriver | Where-Object { $_.Name -eq "WinFsp.Launcher" }
        if ($driver) {
            Write-Host "   ✓ Driver WinFsp.Launcher: $($driver.State)" -ForegroundColor Green
        }
        break
    }
}

if (-not $winfspFound) {
    Write-Host "   ✗ WinFsp NO está instalado" -ForegroundColor Red
    Write-Host ""
    Write-Host "   WinFsp es REQUERIDO para montar unidades en Windows" -ForegroundColor Yellow
    Write-Host "   Descárgalo desde: https://winfsp.dev/rel/" -ForegroundColor Cyan
    Write-Host "   Instala: winfsp-2.0.23075.msi (o versión más reciente)" -ForegroundColor Cyan
    Write-Host ""
}

# 4. Verificar configuración de rclone
Write-Host ""
Write-Host "4. Verificando configuración de rclone..." -ForegroundColor Yellow
$rcloneConfigPath = "$env:USERPROFILE\.config\rclone\rclone.conf"
if (Test-Path $rcloneConfigPath) {
    Write-Host "   ✓ Archivo de configuración existe" -ForegroundColor Green
    Write-Host "   Ubicación: $rcloneConfigPath" -ForegroundColor Gray
    
    # Mostrar perfiles configurados
    $content = Get-Content $rcloneConfigPath
    $profiles = $content | Select-String -Pattern '^\[(.+)\]' | ForEach-Object { $_.Matches.Groups[1].Value }
    if ($profiles) {
        Write-Host "   Perfiles configurados:" -ForegroundColor Cyan
        foreach ($profile in $profiles) {
            Write-Host "     - $profile" -ForegroundColor White
        }
    }
} else {
    Write-Host "   ⚠ No hay configuración de rclone aún" -ForegroundColor Yellow
    Write-Host "   Se creará al configurar un perfil en la aplicación" -ForegroundColor Gray
}

Write-Host ""
Write-Host "=== Resumen ===" -ForegroundColor Cyan
if ($rcloneFound -and $winfspFound) {
    Write-Host "✓ Sistema listo para montar unidades" -ForegroundColor Green
} elseif ($rcloneFound -and -not $winfspFound) {
    Write-Host "⚠ FALTA WinFsp - Instálalo para poder montar unidades" -ForegroundColor Yellow
} else {
    Write-Host "✗ Configuración incompleta" -ForegroundColor Red
}

Write-Host ""
Write-Host "Presiona cualquier tecla para continuar..."
$null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
