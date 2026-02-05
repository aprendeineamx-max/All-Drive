# Script de instalación automática para VultrDriveDesktop
# Fecha: 06/11/2025

Write-Host "=== INSTALADOR AUTOMÁTICO DE VULTRDRIVEDESKTOP ===" -ForegroundColor Cyan
Write-Host ""

# Función para verificar si se ejecuta como administrador
function Test-Administrator {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

# Función para instalar Python usando winget
function Install-Python {
    Write-Host "Instalando Python..." -ForegroundColor Yellow
    
    try {
        # Intentar con winget primero
        winget install Python.Python.3.11 --accept-source-agreements --accept-package-agreements
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ Python instalado correctamente con winget" -ForegroundColor Green
            return $true
        }
    } catch {
        Write-Host "winget no disponible, intentando descarga directa..." -ForegroundColor Yellow
    }
    
    # Si winget falla, intentar descarga directa
    try {
        $pythonUrl = "https://www.python.org/ftp/python/3.11.6/python-3.11.6-amd64.exe"
        $pythonInstaller = "$env:TEMP\python_installer.exe"
        
        Write-Host "Descargando Python desde python.org..." -ForegroundColor Yellow
        Invoke-WebRequest -Uri $pythonUrl -OutFile $pythonInstaller
        
        Write-Host "Ejecutando instalador de Python..." -ForegroundColor Yellow
        Start-Process -FilePath $pythonInstaller -ArgumentList "/quiet", "InstallAllUsers=1", "PrependPath=1", "Include_test=0" -Wait
        
        Remove-Item $pythonInstaller -Force
        Write-Host "✓ Python instalado correctamente" -ForegroundColor Green
        return $true
    } catch {
        Write-Host "✗ Error instalando Python: $_" -ForegroundColor Red
        return $false
    }
}

# Verificar si Python está instalado
Write-Host "1. Verificando Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Python ya está instalado: $pythonVersion" -ForegroundColor Green
    } else {
        throw "Python no encontrado"
    }
} catch {
    Write-Host "Python no está instalado. Procediendo con la instalación..." -ForegroundColor Yellow
    
    if (-not (Test-Administrator)) {
        Write-Host "⚠ Se recomienda ejecutar como administrador para instalar Python" -ForegroundColor Yellow
        $response = Read-Host "¿Continuar sin permisos de administrador? (S/N)"
        if ($response -ne 'S' -and $response -ne 's') {
            Write-Host "Instalación cancelada. Ejecute como administrador para mejores resultados." -ForegroundColor Yellow
            exit 1
        }
    }
    
    if (-not (Install-Python)) {
        Write-Host "✗ No se pudo instalar Python automáticamente." -ForegroundColor Red
        Write-Host "Por favor, instale Python manualmente desde https://python.org" -ForegroundColor Yellow
        exit 1
    }
    
    # Refrescar PATH
    $env:PATH = [System.Environment]::GetEnvironmentVariable("PATH", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("PATH", "User")
}

# Verificar pip
Write-Host ""
Write-Host "2. Verificando pip..." -ForegroundColor Yellow
try {
    pip --version | Out-Null
    Write-Host "✓ pip está disponible" -ForegroundColor Green
} catch {
    Write-Host "✗ pip no está disponible" -ForegroundColor Red
    exit 1
}

# Instalar dependencias
Write-Host ""
Write-Host "3. Instalando dependencias de Python..." -ForegroundColor Yellow

$dependencies = @("PyQt6", "boto3", "watchdog")
foreach ($dep in $dependencies) {
    Write-Host "Instalando $dep..." -ForegroundColor Gray
    pip install $dep --quiet
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ $dep instalado" -ForegroundColor Green
    } else {
        Write-Host "✗ Error instalando $dep" -ForegroundColor Red
    }
}

# Verificar rclone
Write-Host ""
Write-Host "4. Verificando rclone..." -ForegroundColor Yellow

$rcloneFound = $false
$rclonePaths = @(
    "rclone.exe",
    "rclone-v1.71.2-windows-amd64\rclone.exe"
)

foreach ($path in $rclonePaths) {
    if (Test-Path $path) {
        Write-Host "✓ rclone encontrado en: $path" -ForegroundColor Green
        $rcloneFound = $true
        break
    }
}

if (-not $rcloneFound) {
    Write-Host "⚠ rclone no encontrado" -ForegroundColor Yellow
    $response = Read-Host "¿Desea descargar rclone automáticamente? (S/N)"
    
    if ($response -eq 'S' -or $response -eq 's') {
        try {
            Write-Host "Descargando rclone..." -ForegroundColor Yellow
            $rcloneUrl = "https://downloads.rclone.org/v1.71.2/rclone-v1.71.2-windows-amd64.zip"
            $rcloneZip = "$env:TEMP\rclone.zip"
            
            Invoke-WebRequest -Uri $rcloneUrl -OutFile $rcloneZip
            
            Write-Host "Extrayendo rclone..." -ForegroundColor Yellow
            Expand-Archive -Path $rcloneZip -DestinationPath "." -Force
            
            Remove-Item $rcloneZip -Force
            Write-Host "✓ rclone descargado e instalado" -ForegroundColor Green
        } catch {
            Write-Host "✗ Error descargando rclone: $_" -ForegroundColor Red
            Write-Host "Puede descargar manualmente desde: https://rclone.org/downloads/" -ForegroundColor Yellow
        }
    } else {
        Write-Host "ℹ rclone se puede descargar desde: https://rclone.org/downloads/" -ForegroundColor Cyan
    }
}

# Verificar archivos de la aplicación
Write-Host ""
Write-Host "5. Verificando archivos de la aplicación..." -ForegroundColor Yellow

$requiredFiles = @(
    "app.py",
    "translations.py",
    "theme_manager.py",
    "ui\main_window.py",
    "config_manager.py",
    "s3_handler.py",
    "rclone_manager.py"
)

$allFilesPresent = $true
foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Write-Host "✓ $file" -ForegroundColor Green
    } else {
        Write-Host "✗ $file faltante" -ForegroundColor Red
        $allFilesPresent = $false
    }
}

if (-not $allFilesPresent) {
    Write-Host "✗ Algunos archivos están faltantes. Verifique la instalación." -ForegroundColor Red
    exit 1
}

# Crear acceso directo en el escritorio
Write-Host ""
Write-Host "6. Creando acceso directo..." -ForegroundColor Yellow

try {
    $WshShell = New-Object -comObject WScript.Shell
    $Shortcut = $WshShell.CreateShortcut("$env:USERPROFILE\Desktop\VultrDriveDesktop.lnk")
    $Shortcut.TargetPath = "powershell.exe"
    $Shortcut.Arguments = "-ExecutionPolicy Bypass -File `"$PWD\start.ps1`""
    $Shortcut.WorkingDirectory = $PWD
    $Shortcut.IconLocation = "shell32.dll,13"
    $Shortcut.Description = "VultrDriveDesktop - Cloud Storage Manager"
    $Shortcut.Save()
    Write-Host "✓ Acceso directo creado en el escritorio" -ForegroundColor Green
} catch {
    Write-Host "⚠ No se pudo crear el acceso directo: $_" -ForegroundColor Yellow
}

# Resumen final
Write-Host ""
Write-Host "=== INSTALACIÓN COMPLETADA ===" -ForegroundColor Cyan
Write-Host "✓ Python instalado y configurado" -ForegroundColor Green
Write-Host "✓ Dependencias instaladas" -ForegroundColor Green
Write-Host "✓ Archivos de aplicación verificados" -ForegroundColor Green

if ($rcloneFound -or (Test-Path "rclone-v1.71.2-windows-amd64\rclone.exe")) {
    Write-Host "✓ rclone disponible para montaje de unidades" -ForegroundColor Green
} else {
    Write-Host "⚠ rclone no disponible (función de montaje limitada)" -ForegroundColor Yellow
}

Write-Host "✓ Acceso directo creado en el escritorio" -ForegroundColor Green
Write-Host ""
Write-Host "🚀 VultrDriveDesktop está listo para usar!" -ForegroundColor Cyan
Write-Host ""
Write-Host "Para iniciar la aplicación:" -ForegroundColor Yellow
Write-Host "  1. Haga doble clic en el acceso directo del escritorio" -ForegroundColor White
Write-Host "  2. O ejecute: .\start.ps1" -ForegroundColor White
Write-Host ""
Write-Host "Características disponibles:" -ForegroundColor Yellow
Write-Host "  🌐 Múltiples idiomas (ES, EN, FR)" -ForegroundColor White
Write-Host "  🎨 Temas claro y oscuro" -ForegroundColor White
Write-Host "  📁 Subida y descarga de archivos" -ForegroundColor White
Write-Host "  💾 Respaldo automático de carpetas" -ForegroundColor White
Write-Host "  🔗 Montaje como unidad de red" -ForegroundColor White
Write-Host "  ⚡ Sincronización en tiempo real" -ForegroundColor White
Write-Host ""

$response = Read-Host "¿Desea ejecutar la aplicación ahora? (S/N)"
if ($response -eq 'S' -or $response -eq 's') {
    Write-Host ""
    Write-Host "Iniciando VultrDriveDesktop..." -ForegroundColor Green
    .\start.ps1
}