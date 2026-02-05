# ====================================
#  SCRIPT COMPLETO: Compilar y ZIP
# ====================================
# VultrDriveDesktop - Compilación Automática
# Usa este script para compilar y crear el ZIP en un solo paso

Write-Host "`n=== COMPILACION Y EMPAQUETADO ===" -ForegroundColor Cyan
Write-Host "VultrDriveDesktop v2.0 - Con Traducciones Completas`n" -ForegroundColor White

# 1. Compilar con EMPAQUETAR.bat
Write-Host "1. Compilando aplicación..." -ForegroundColor Yellow
Write-Host "   (Esto puede tardar 2-5 minutos)`n" -ForegroundColor Gray

.\EMPAQUETAR.bat

if (-not (Test-Path "VultrDriveDesktop-Portable\VultrDriveDesktop.exe")) {
    Write-Host "`n❌ ERROR: La compilación falló" -ForegroundColor Red
    Write-Host "   Verifica que PyInstaller esté instalado: pip install pyinstaller`n" -ForegroundColor Yellow
    exit 1
}

Write-Host "`n✅ Compilación exitosa`n" -ForegroundColor Green

# 2. Crear ZIP
Write-Host "2. Creando archivo ZIP..." -ForegroundColor Yellow

if (Test-Path "VultrDriveDesktop-Portable.zip") { 
    Write-Host "   Eliminando ZIP anterior..." -ForegroundColor Gray
    Remove-Item "VultrDriveDesktop-Portable.zip" -Force 
}

Write-Host "   Comprimiendo archivos..." -ForegroundColor Gray
Compress-Archive -Path "VultrDriveDesktop-Portable\*" `
                 -DestinationPath "VultrDriveDesktop-Portable.zip" `
                 -Force

Write-Host "`n✅ ZIP creado exitosamente`n" -ForegroundColor Green

# 3. Mostrar resultados
Write-Host "=== RESULTADOS ===" -ForegroundColor Cyan

Write-Host "`n📁 Carpeta Portable:" -ForegroundColor Yellow
Get-ChildItem "VultrDriveDesktop-Portable" | 
    Select-Object Name, LastWriteTime, @{Name="Tamaño (MB)";Expression={[math]::Round($_.Length/1MB,2)}} | 
    Format-Table -AutoSize

Write-Host "📦 Archivo ZIP:" -ForegroundColor Yellow
Get-Item "VultrDriveDesktop-Portable.zip" | 
    Select-Object Name, LastWriteTime, @{Name="Tamaño (MB)";Expression={[math]::Round($_.Length/1MB,2)}} | 
    Format-Table -AutoSize

Write-Host "✅ PROCESO COMPLETADO" -ForegroundColor Green
Write-Host "`nArchivos listos para distribuir:" -ForegroundColor White
Write-Host "  1. Carpeta: .\VultrDriveDesktop-Portable\" -ForegroundColor Cyan
Write-Host "  2. ZIP:     .\VultrDriveDesktop-Portable.zip`n" -ForegroundColor Cyan
