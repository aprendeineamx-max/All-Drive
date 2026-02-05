# Script de Verificación para VultrDrive Desktop Portable
# Verifica que todos los componentes necesarios estén presentes

param(
    [switch]$DescargarWinFsp
)

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "   VERIFICADOR DE COMPONENTES - VultrDrive Desktop Portable" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

$baseDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$errores = 0
$advertencias = 0

# Función para verificar archivo
function Test-Archivo {
    param(
        [string]$ruta,
        [string]$nombre,
        [bool]$critico = $true
    )
    
    if (Test-Path $ruta) {
        $sizeMB = (Get-Item $ruta).Length / 1MB
        Write-Host "  ✓ $nombre" -ForegroundColor Green
        Write-Host "    Ubicacion: $ruta" -ForegroundColor Gray
        Write-Host "    Tamano: $([math]::Round($sizeMB, 2)) MB" -ForegroundColor Gray
        return $true
    } else {
        if ($critico) {
            Write-Host "  ✗ $nombre - NO ENCONTRADO" -ForegroundColor Red
            Write-Host "    Se esperaba en: $ruta" -ForegroundColor Gray
            $script:errores++
        } else {
            Write-Host "  ⚠ $nombre - No encontrado (opcional)" -ForegroundColor Yellow
            Write-Host "    Se esperaba en: $ruta" -ForegroundColor Gray
            $script:advertencias++
        }
        return $false
    }
}

# Función para verificar carpeta
function Test-Carpeta {
    param(
        [string]$ruta,
        [string]$nombre
    )
    
    if (Test-Path $ruta -PathType Container) {
        $archivos = (Get-ChildItem $ruta -File -Recurse).Count
        Write-Host "  ✓ $nombre" -ForegroundColor Green
        Write-Host "    Ubicación: $ruta" -ForegroundColor Gray
        Write-Host "    Archivos: $archivos" -ForegroundColor Gray
        return $true
    } else {
        Write-Host "  ✗ $nombre - NO ENCONTRADA" -ForegroundColor Red
        Write-Host "    Se esperaba en: $ruta" -ForegroundColor Gray
        $script:errores++
        return $false
    }
}

Write-Host "[1/5] Verificando archivos principales..." -ForegroundColor Cyan
Write-Host ""
Test-Archivo "$baseDir\app.py" "Programa principal (app.py)" $true
Test-Archivo "$baseDir\ejecutar_app.bat" "Script de ejecución (ejecutar_app.bat)" $true
Test-Archivo "$baseDir\config.json" "Configuración (config.json)" $false
Test-Archivo "$baseDir\requirements.txt" "Dependencias Python (requirements.txt)" $true

Write-Host ""
Write-Host "[2/5] Verificando interfaz de usuario..." -ForegroundColor Cyan
Write-Host ""
Test-Carpeta "$baseDir\ui" "Carpeta UI"
if (Test-Path "$baseDir\ui") {
    Test-Archivo "$baseDir\ui\main_window.py" "Ventana principal" $true
    Test-Archivo "$baseDir\ui\settings_window.py" "Ventana de configuración" $false
}

Write-Host ""
Write-Host "[3/5] Verificando Rclone..." -ForegroundColor Cyan
Write-Host ""
$rcloneDirs = Get-ChildItem "$baseDir" -Directory | Where-Object { $_.Name -like "rclone*" }
if ($rcloneDirs.Count -gt 0) {
    $rcloneDir = $rcloneDirs[0].FullName
    Test-Archivo "$rcloneDir\rclone.exe" "Rclone ejecutable" $true
} else {
    Write-Host "  ✗ Carpeta de Rclone - NO ENCONTRADA" -ForegroundColor Red
    Write-Host "    Se esperaba: rclone-vX.XX.X-windows-amd64\" -ForegroundColor Gray
    $script:errores++
}

Write-Host ""
Write-Host "[4/5] Verificando instalador de WinFsp..." -ForegroundColor Cyan
Write-Host ""

# Verificar carpeta dependencies
$depDir = "$baseDir\dependencies"
if (-not (Test-Path $depDir)) {
    Write-Host "  ℹ Creando carpeta dependencies..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Path $depDir -Force | Out-Null
}

# Buscar instalador de WinFsp
$winfspMsi = Get-ChildItem "$depDir" -Filter "winfsp*.msi" -ErrorAction SilentlyContinue
if ($winfspMsi) {
    $winfspPath = $winfspMsi[0].FullName
    Test-Archivo $winfspPath "Instalador WinFsp MSI" $true
} else {
    Write-Host "  ✗ Instalador WinFsp - NO ENCONTRADO" -ForegroundColor Red
    Write-Host "    Se esperaba: $depDir\winfsp-*.msi" -ForegroundColor Gray
    $script:errores++
    
    if ($DescargarWinFsp) {
        Write-Host ""
        Write-Host "  → Descargando WinFsp automáticamente..." -ForegroundColor Yellow
        $winfspUrl = "https://github.com/winfsp/winfsp/releases/download/v2.0/winfsp-2.0.23075.msi"
        $winfspDest = "$depDir\winfsp-2.0.23075.msi"
        
        try {
            [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
            $ProgressPreference = 'SilentlyContinue'
            Invoke-WebRequest -Uri $winfspUrl -OutFile $winfspDest
            
            if (Test-Path $winfspDest) {
                Write-Host "  ✓ WinFsp descargado exitosamente" -ForegroundColor Green
                $script:errores--
            }
        } catch {
            Write-Host "  ✗ Error al descargar: $_" -ForegroundColor Red
        }
    } else {
        Write-Host ""
        Write-Host "  💡 SOLUCIÓN: Ejecuta este script con el parámetro -DescargarWinFsp" -ForegroundColor Yellow
        Write-Host "     Ejemplo: .\verificar_portable.ps1 -DescargarWinFsp" -ForegroundColor Gray
    }
}

Write-Host ""
Write-Host "[5/5] Verificando componentes adicionales..." -ForegroundColor Cyan
Write-Host ""
Test-Archivo "$baseDir\theme_manager.py" "Gestor de temas" $false
Test-Archivo "$baseDir\translations.py" "Sistema de traducciones" $false
Test-Archivo "$baseDir\rclone_manager.py" "Gestor de Rclone" $true
Test-Archivo "$baseDir\config_manager.py" "Gestor de configuración" $true

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "                     RESUMEN DE VERIFICACIÓN" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

if ($errores -eq 0 -and $advertencias -eq 0) {
    Write-Host "  ✓ TODO ESTÁ LISTO" -ForegroundColor Green
    Write-Host "  ✓ El programa está completo y es 100% portable" -ForegroundColor Green
    Write-Host ""
    Write-Host "  Puedes copiar toda la carpeta a cualquier PC y funcionará." -ForegroundColor Gray
    Write-Host "  WinFsp se instalará automáticamente la primera vez." -ForegroundColor Gray
} elseif ($errores -eq 0) {
    Write-Host "  ✓ LISTO CON ADVERTENCIAS" -ForegroundColor Yellow
    Write-Host "  ⚠ $advertencias componentes opcionales no encontrados" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  El programa funcionará, pero algunas características pueden" -ForegroundColor Gray
    Write-Host "  no estar disponibles." -ForegroundColor Gray
} else {
    Write-Host "  ✗ SE ENCONTRARON PROBLEMAS" -ForegroundColor Red
    Write-Host "  ✗ Errores críticos: $errores" -ForegroundColor Red
    if ($advertencias -gt 0) {
        Write-Host "  ⚠ Advertencias: $advertencias" -ForegroundColor Yellow
    }
    Write-Host ""
    Write-Host "  El programa NO funcionará correctamente hasta resolver" -ForegroundColor Gray
    Write-Host "  los errores marcados arriba." -ForegroundColor Gray
}

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Verificar si WinFsp está instalado en el sistema
Write-Host "🔍 Verificando instalación de WinFsp en el sistema..." -ForegroundColor Cyan
$winfspPaths = @(
    "C:\Program Files (x86)\WinFsp\bin\winfsp-x64.dll",
    "C:\Program Files\WinFsp\bin\winfsp-x64.dll"
)

$winfspInstalado = $false
foreach ($path in $winfspPaths) {
    if (Test-Path $path) {
        Write-Host "  ✓ WinFsp YA ESTÁ INSTALADO en este sistema" -ForegroundColor Green
        Write-Host "    Ubicación: $path" -ForegroundColor Gray
        $winfspInstalado = $true
        break
    }
}

if (-not $winfspInstalado) {
    Write-Host "  ℹ WinFsp NO está instalado en este sistema" -ForegroundColor Yellow
    Write-Host "    Se instalará automáticamente al ejecutar el programa" -ForegroundColor Gray
}

Write-Host ""
Write-Host "📚 Documentación disponible:" -ForegroundColor Cyan
if (Test-Path "$baseDir\INSTALACION_AUTOMATICA_WINFSP.md") {
    Write-Host "  → INSTALACION_AUTOMATICA_WINFSP.md - Guía del sistema portable" -ForegroundColor Gray
}
if (Test-Path "$baseDir\README.md") {
    Write-Host "  → README.md - Documentación general" -ForegroundColor Gray
}

Write-Host ""
pause

