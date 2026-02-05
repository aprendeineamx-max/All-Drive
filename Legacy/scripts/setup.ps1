# Instalador Simple de Python y Dependencias para VultrDriveDesktop
# Fecha: 06/11/2025

Write-Host ""
Write-Host "=================================" -ForegroundColor Cyan
Write-Host " INSTALADOR VULTRDRIVEDESKTOP" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan
Write-Host ""

# Verificar si Python está instalado
Write-Host "[1/4] Verificando Python..." -ForegroundColor Yellow

$pythonFound = $false
$pythonCmd = ""

# Intentar py (Python Launcher de Windows)
try {
    $version = py --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  OK: Python encontrado - $version" -ForegroundColor Green
        $pythonFound = $true
        $pythonCmd = "py"
    }
} catch {}

# Si no, intentar python
if (-not $pythonFound) {
    try {
        $version = python --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  OK: Python encontrado - $version" -ForegroundColor Green
            $pythonFound = $true
            $pythonCmd = "python"
        }
    } catch {}
}

# Si no hay Python, dar instrucciones
if (-not $pythonFound) {
    Write-Host "  ERROR: Python no encontrado" -ForegroundColor Red
    Write-Host ""
    Write-Host "  Para instalar Python, elija una opcion:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  OPCION 1 - Microsoft Store (Recomendada):" -ForegroundColor Cyan
    Write-Host "    1. Abrir Microsoft Store" -ForegroundColor White
    Write-Host "    2. Buscar 'Python 3.11'" -ForegroundColor White
    Write-Host "    3. Instalar" -ForegroundColor White
    Write-Host ""
    Write-Host "  OPCION 2 - Descarga Directa:" -ForegroundColor Cyan
    Write-Host "    Visite: https://www.python.org/downloads/" -ForegroundColor White
    Write-Host "    Descargue e instale Python 3.11 o superior" -ForegroundColor White
    Write-Host "    IMPORTANTE: Marcar 'Add Python to PATH'" -ForegroundColor Yellow
    Write-Host ""
    
    $response = Read-Host "Abrir Microsoft Store ahora? (S/N)"
    if ($response -eq 'S' -or $response -eq 's') {
        Start-Process "ms-windows-store://pdp/?productid=9PJPW5LDXLZ5"
    }
    
    Write-Host ""
    Write-Host "Una vez instalado Python, ejecute este script nuevamente." -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Presione Enter para salir"
    exit 1
}

# Verificar pip
Write-Host ""
Write-Host "[2/4] Verificando pip..." -ForegroundColor Yellow

try {
    & $pythonCmd -m pip --version | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  OK: pip esta disponible" -ForegroundColor Green
    } else {
        throw "pip no funciona"
    }
} catch {
    Write-Host "  Instalando pip..." -ForegroundColor Yellow
    & $pythonCmd -m ensurepip --default-pip
    & $pythonCmd -m pip install --upgrade pip
}

# Instalar dependencias
Write-Host ""
Write-Host "[3/4] Instalando dependencias..." -ForegroundColor Yellow

$dependencies = @(
    @{Name="PyQt6"; Package="PyQt6"},
    @{Name="boto3"; Package="boto3"},
    @{Name="watchdog"; Package="watchdog"}
)

foreach ($dep in $dependencies) {
    Write-Host "  Instalando $($dep.Name)..." -ForegroundColor Gray
    
    try {
        & $pythonCmd -m pip install $($dep.Package) --quiet --disable-pip-version-check
        if ($LASTEXITCODE -eq 0) {
            Write-Host "    OK: $($dep.Name) instalado" -ForegroundColor Green
        } else {
            Write-Host "    ERROR instalando $($dep.Name)" -ForegroundColor Red
        }
    } catch {
        Write-Host "    ERROR: $_" -ForegroundColor Red
    }
}

# Verificar rclone
Write-Host ""
Write-Host "[4/4] Verificando rclone..." -ForegroundColor Yellow

$rclonePath = $null

# Buscar rclone
if (Test-Path "rclone.exe") {
    $rclonePath = "rclone.exe"
} elseif (Test-Path "rclone-v1.71.2-windows-amd64\rclone.exe") {
    $rclonePath = "rclone-v1.71.2-windows-amd64\rclone.exe"
}

if ($rclonePath) {
    Write-Host "  OK: rclone encontrado en $rclonePath" -ForegroundColor Green
} else {
    Write-Host "  AVISO: rclone no encontrado" -ForegroundColor Yellow
    Write-Host "    La funcion de montaje no estara disponible." -ForegroundColor Gray
    Write-Host ""
    
    $response = Read-Host "  Descargar rclone ahora? (S/N)"
    if ($response -eq 'S' -or $response -eq 's') {
        Write-Host "  Descargando rclone..." -ForegroundColor Yellow
        
        try {
            $url = "https://downloads.rclone.org/v1.65.0/rclone-v1.65.0-windows-amd64.zip"
            $output = "$env:TEMP\rclone.zip"
            
            # Descargar
            Invoke-WebRequest -Uri $url -OutFile $output -UseBasicParsing
            
            # Extraer
            Expand-Archive -Path $output -DestinationPath "." -Force
            
            # Limpiar
            Remove-Item $output -Force
            
            Write-Host "    OK: rclone descargado e instalado" -ForegroundColor Green
        } catch {
            Write-Host "    ERROR: No se pudo descargar rclone" -ForegroundColor Red
            Write-Host "    Puede descargarlo manualmente desde: https://rclone.org/downloads/" -ForegroundColor Yellow
        }
    }
}

# Crear acceso directo
Write-Host ""
Write-Host "Creando acceso directo..." -ForegroundColor Yellow

try {
    $desktopPath = [Environment]::GetFolderPath("Desktop")
    $shortcutPath = "$desktopPath\VultrDriveDesktop.lnk"
    
    $WshShell = New-Object -ComObject WScript.Shell
    $Shortcut = $WshShell.CreateShortcut($shortcutPath)
    $Shortcut.TargetPath = "powershell.exe"
    $Shortcut.Arguments = "-ExecutionPolicy Bypass -WindowStyle Hidden -File `"$PSScriptRoot\start.ps1`""
    $Shortcut.WorkingDirectory = $PSScriptRoot
    $Shortcut.Description = "VultrDriveDesktop - Cloud Storage Manager"
    $Shortcut.Save()
    
    Write-Host "  OK: Acceso directo creado en el escritorio" -ForegroundColor Green
} catch {
    Write-Host "  AVISO: No se pudo crear acceso directo" -ForegroundColor Yellow
}

# Resumen final
Write-Host ""
Write-Host "=================================" -ForegroundColor Cyan
Write-Host " INSTALACION COMPLETADA" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "VultrDriveDesktop esta listo para usar!" -ForegroundColor Green
Write-Host ""
Write-Host "Caracteristicas:" -ForegroundColor Yellow
Write-Host "  - Multiples idiomas (ES, EN, FR)" -ForegroundColor White
Write-Host "  - Temas claro y oscuro" -ForegroundColor White
Write-Host "  - Subida y respaldo de archivos" -ForegroundColor White
Write-Host "  - Sincronizacion en tiempo real" -ForegroundColor White

if ($rclonePath -or (Test-Path "rclone-v1.65.0-windows-amd64\rclone.exe")) {
    Write-Host "  - Montaje como unidad de red" -ForegroundColor White
}

Write-Host ""
Write-Host "Para iniciar:" -ForegroundColor Yellow
Write-Host "  - Doble clic en el acceso directo del escritorio" -ForegroundColor White
Write-Host "  - O ejecute: .\start.ps1" -ForegroundColor White
Write-Host ""

$response = Read-Host "Iniciar VultrDriveDesktop ahora? (S/N)"
if ($response -eq 'S' -or $response -eq 's') {
    Write-Host ""
    Write-Host "Iniciando aplicacion..." -ForegroundColor Green
    & $pythonCmd app.py
}