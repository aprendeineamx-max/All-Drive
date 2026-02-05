# Script de Verificacion Rapida para VultrDriveDesktop

Write-Host ""
Write-Host "=================================" -ForegroundColor Cyan
Write-Host " VERIFICACION DEL SISTEMA" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan
Write-Host ""

$errorsFound = $false

# 1. Verificar Python
Write-Host "[1/5] Python..." -ForegroundColor Yellow
$pythonCmd = $null
$pythonVer = $null

foreach ($cmd in @("py", "python", "python3")) {
    try {
        $ver = & $cmd --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            $pythonCmd = $cmd
            $pythonVer = $ver
            break
        }
    } catch {}
}

if ($pythonCmd) {
    Write-Host "  OK: $pythonVer" -ForegroundColor Green
    Write-Host "      Comando: $pythonCmd" -ForegroundColor Gray
} else {
    Write-Host "  ERROR: Python no esta instalado" -ForegroundColor Red
    Write-Host "         Instale desde: https://www.python.org/downloads/" -ForegroundColor Yellow
    $errorsFound = $true
}

# 2. Verificar dependencias Python
Write-Host ""
Write-Host "[2/5] Dependencias Python..." -ForegroundColor Yellow

if ($pythonCmd) {
    $deps = @("PyQt6", "boto3", "watchdog")
    foreach ($dep in $deps) {
        try {
            & $pythonCmd -c "import $($dep.ToLower())" 2>$null
            if ($LASTEXITCODE -eq 0) {
                Write-Host "  OK: $dep" -ForegroundColor Green
            } else {
                Write-Host "  ERROR: $dep no instalado" -ForegroundColor Red
                Write-Host "         Ejecute: $pythonCmd -m pip install $dep" -ForegroundColor Yellow
                $errorsFound = $true
            }
        } catch {
            Write-Host "  ERROR: $dep no instalado" -ForegroundColor Red
            $errorsFound = $true
        }
    }
} else {
    Write-Host "  OMITIDO: Python no disponible" -ForegroundColor Gray
}

# 3. Verificar rclone
Write-Host ""
Write-Host "[3/5] rclone (opcional)..." -ForegroundColor Yellow

$rclonePaths = @(
    "rclone.exe",
    "rclone-v1.71.2-windows-amd64\rclone.exe",
    "rclone-v1.65.0-windows-amd64\rclone.exe"
)

$rcloneFound = $false
foreach ($path in $rclonePaths) {
    if (Test-Path $path) {
        Write-Host "  OK: Encontrado en $path" -ForegroundColor Green
        $rcloneFound = $true
        break
    }
}

if (-not $rcloneFound) {
    Write-Host "  AVISO: rclone no encontrado" -ForegroundColor Yellow
    Write-Host "         La funcion de montaje no estara disponible" -ForegroundColor Gray
    Write-Host "         Descargue desde: https://rclone.org/downloads/" -ForegroundColor Gray
}

# 4. Verificar archivos de la aplicacion
Write-Host ""
Write-Host "[4/5] Archivos de la aplicacion..." -ForegroundColor Yellow

$requiredFiles = @(
    "app.py",
    "translations.py",
    "theme_manager.py",
    "config_manager.py",
    "s3_handler.py",
    "rclone_manager.py",
    "file_watcher.py",
    "ui\main_window.py",
    "ui\settings_window.py"
)

$allFilesPresent = $true
foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Write-Host "  OK: $file" -ForegroundColor Green
    } else {
        Write-Host "  ERROR: $file faltante" -ForegroundColor Red
        $allFilesPresent = $false
        $errorsFound = $true
    }
}

# 5. Verificar preferencias de usuario
Write-Host ""
Write-Host "[5/5] Configuracion de usuario..." -ForegroundColor Yellow

if (Test-Path "user_preferences.json") {
    try {
        $prefs = Get-Content "user_preferences.json" | ConvertFrom-Json
        Write-Host "  OK: Preferencias encontradas" -ForegroundColor Green
        Write-Host "      Idioma: $($prefs.language)" -ForegroundColor Gray
        Write-Host "      Tema: $($prefs.theme)" -ForegroundColor Gray
    } catch {
        Write-Host "  AVISO: Archivo de preferencias corrupto" -ForegroundColor Yellow
        Write-Host "         Se creara uno nuevo al iniciar" -ForegroundColor Gray
    }
} else {
    Write-Host "  INFO: Sin preferencias (primera ejecucion)" -ForegroundColor Cyan
    Write-Host "        Se crearan automaticamente al iniciar" -ForegroundColor Gray
}

# Verificar perfiles
if (Test-Path "config.json") {
    try {
        $config = Get-Content "config.json" | ConvertFrom-Json
        $profileCount = ($config.profiles | Get-Member -MemberType NoteProperty).Count
        Write-Host "  INFO: $profileCount perfil(es) configurado(s)" -ForegroundColor Cyan
    } catch {}
}

# Resumen final
Write-Host ""
Write-Host "=================================" -ForegroundColor Cyan
Write-Host " RESUMEN" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan
Write-Host ""

if (-not $errorsFound) {
    Write-Host "TODO OK!" -ForegroundColor Green
    Write-Host ""
    Write-Host "La aplicacion esta lista para usarse." -ForegroundColor Green
    Write-Host ""
    Write-Host "Para iniciar:" -ForegroundColor Yellow
    Write-Host "  - Ejecute: .\start.bat" -ForegroundColor White
    Write-Host "  - O ejecute: .\start.ps1" -ForegroundColor White
    
    if ($pythonCmd) {
        Write-Host "  - O ejecute: $pythonCmd app.py" -ForegroundColor White
    }
} else {
    Write-Host "SE ENCONTRARON PROBLEMAS" -ForegroundColor Red
    Write-Host ""
    Write-Host "Por favor, corrija los errores marcados arriba." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Para instalar dependencias faltantes:" -ForegroundColor Yellow
    Write-Host "  Ejecute: .\setup.ps1" -ForegroundColor White
    Write-Host ""
    Write-Host "Para mas ayuda, consulte: SOLUCION_PROBLEMAS.md" -ForegroundColor Cyan
}

Write-Host ""
Read-Host "Presione Enter para salir"