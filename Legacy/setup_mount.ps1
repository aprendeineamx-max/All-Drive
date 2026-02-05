$ErrorActionPreference = "Stop"

# URLs
$RcloneUrl = "https://downloads.rclone.org/rclone-current-windows-amd64.zip"
$WinFspUrl = "https://github.com/winfsp/winfsp/releases/download/v2.0/winfsp-2.0.23075.msi"

# Paths
$WorkDir = $PSScriptRoot
$RcloneZip = "$WorkDir\rclone.zip"
$RcloneDir = "$WorkDir\rclone-bin"
$WinFspMsi = "$WorkDir\winfsp.msi"
$RcloneConfig = "$WorkDir\rclone.conf"

Write-Host "Iniciando configuración..."

# 1. Download and Install WinFsp
if (!(Get-Command "mount" -ErrorAction SilentlyContinue)) { # Crude check, better to check registry or assume install needed
    Write-Host "Descargando WinFsp..."
    Invoke-WebRequest -Uri $WinFspUrl -OutFile $WinFspMsi
    
    Write-Host "Instalando WinFsp (Requiere elevación)..."
    Start-Process -FilePath "msiexec.exe" -ArgumentList "/i `"$WinFspMsi`" /qn" -Wait -Verb RunAs
    Write-Host "WinFsp instalado."
} else {
    Write-Host "WinFsp parece estar presente (o comando mount existe)."
}

# 2. Download and Setup Rclone
if (!(Test-Path "$RcloneDir\rclone.exe")) {
    Write-Host "Descargando Rclone..."
    Invoke-WebRequest -Uri $RcloneUrl -OutFile $RcloneZip
    
    Write-Host "Extrayendo Rclone..."
    Expand-Archive -Path $RcloneZip -DestinationPath "$WorkDir\rclone-temp" -Force
    
    # Move the inner folder content to $RcloneDir
    $InnerFolder = Get-ChildItem "$WorkDir\rclone-temp" | Select-Object -First 1
    Move-Item $InnerFolder.FullName $RcloneDir -Force
    Remove-Item "$WorkDir\rclone-temp" -Recurse -Force
    Remove-Item $RcloneZip -Force
    Write-Host "Rclone listo en $RcloneDir"
}

# 3. Create Rclone Config
# Using Dolphin-1000 credentials from previous step
$ConfigContent = @"
[vultr]
type = s3
provider = Vultr
access_key_id = 3Y3MFSZPD8XCC5IMGZWH
secret_access_key = lq95CVjRWqM3CPSXp1Y7P0S8W76bQKz37CtplahX
endpoint = sjc1.vultrobjects.com
acl = private
"@

Set-Content -Path $RcloneConfig -Value $ConfigContent
Write-Host "Configuración de Rclone creada en $RcloneConfig"

# 4. Create Mount Script (Bat)
$MountScript = "$WorkDir\mount_vultr.bat"
$MountCommand = @"
@echo off
cd /d "%~dp0"
echo Montando Vultr Object Storage en Z:...
"%RcloneDir%\rclone.exe" mount vultr: Z: --config "rclone.conf" --vfs-cache-mode full
pause
"@

Set-Content -Path $MountScript -Value $MountCommand
Write-Host "Script de montaje creado: $MountScript"

Write-Host "Instalación completada. Ejecuta '$MountScript' para montar la unidad."
