$ErrorActionPreference = "Stop"

# URLs
$WinFspUrl = "https://github.com/winfsp/winfsp/releases/download/v2.0/winfsp-2.0.23075.msi"

# Paths
$WorkDir = $PSScriptRoot
$WinFspMsi = "$WorkDir\winfsp.msi"

Write-Host "Iniciando instalación forzada de WinFsp..."

# Always download and install to be safe
Write-Host "Descargando WinFsp..."
Invoke-WebRequest -Uri $WinFspUrl -OutFile $WinFspMsi

Write-Host "Instalando WinFsp (Requiere elevación)..."
# Using /qn for quiet install, but we might need /qb to show progress if it hangs
Start-Process -FilePath "msiexec.exe" -ArgumentList "/i `"$WinFspMsi`" /qn" -Wait -Verb RunAs
Write-Host "Instalación de WinFsp completada."
