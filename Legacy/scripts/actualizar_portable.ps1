# Script automatizado para recrear la versión portable y su archivo ZIP
Write-Host "=== Actualizar paquete portable de VultrDriveDesktop ===" -ForegroundColor Cyan

# Cambiar al directorio donde reside este script (raíz del repositorio)
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

$portableFolder = Join-Path $scriptDir 'VultrDriveDesktop-Portable'
$portableZip = Join-Path $scriptDir 'VultrDriveDesktop-Portable.zip'

# Ejecutar el script principal de compilación
Write-Host "1. Construyendo ejecutable portable..." -ForegroundColor Yellow
& .\crear_portable.ps1
if ($LASTEXITCODE -ne 0) {
    Write-Host "   Error: la compilación del portable falló" -ForegroundColor Red
    exit 1
}

# Comprimir el resultado en un ZIP listo para distribución
Write-Host "2. Generando archivo ZIP..." -ForegroundColor Yellow
if (Test-Path $portableZip) {
    Remove-Item $portableZip -Force
}

Compress-Archive -Path (Join-Path $portableFolder '*') -DestinationPath $portableZip -Force

if ($LASTEXITCODE -ne 0 -or -not (Test-Path $portableZip)) {
    Write-Host "   Error: no se pudo crear el archivo ZIP" -ForegroundColor Red
    exit 1
}

$zipSizeMB = [math]::Round(((Get-Item $portableZip).Length / 1MB), 2)
Write-Host "   OK - ZIP creado: $($portableZip) ($zipSizeMB MB)" -ForegroundColor Green

Write-Host "\n=== Proceso completado ===" -ForegroundColor Green
Write-Host "Carpeta portable: $portableFolder"
Write-Host "Archivo ZIP listo para distribuir: $portableZip"
