# Script para crear versión PORTABLE de VultrDrive Desktop
# Solo incluye lo esencial para funcionamiento

$timestamp = Get-Date -Format "yyyyMMdd_HHmm"
$sourcePath = Split-Path -Parent $MyInvocation.MyCommand.Path
$portablePath = Join-Path (Split-Path -Parent $sourcePath) "VultrDrive_Portable_$timestamp"

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  Creando VultrDrive Desktop PORTABLE" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Crear carpeta portable
Write-Host "[1/6] Creando carpeta portable..." -ForegroundColor Yellow
New-Item -ItemType Directory -Path $portablePath -Force | Out-Null
Write-Host "      Creada: $portablePath" -ForegroundColor Green
Write-Host ""

# Copiar archivos Python esenciales
Write-Host "[2/6] Copiando archivos principales..." -ForegroundColor Yellow
$mainFiles = @(
    "app.py",
    "config_manager.py",
    "rclone_manager.py",
    "theme_manager.py",
    "translations.py",
    "translations_base.py",
    "splash_screen.py",
    "s3_handler.py",
    "drive_detector.py",
    "file_watcher.py",
    "ejecutar_app.bat",
    "requirements.txt",
    "LICENSE"
)

foreach ($file in $mainFiles) {
    $srcFile = Join-Path $sourcePath $file
    if (Test-Path $srcFile) {
        Copy-Item $srcFile $portablePath -Force
        Write-Host "      ✓ $file" -ForegroundColor Green
    } else {
        Write-Host "      ✗ $file (no existe)" -ForegroundColor Red
    }
}
Write-Host ""

# Copiar archivos de configuración
Write-Host "[3/6] Copiando configuración..." -ForegroundColor Yellow
$configFiles = @("config.default.json", "config.example.json")
foreach ($file in $configFiles) {
    $srcFile = Join-Path $sourcePath $file
    if (Test-Path $srcFile) {
        Copy-Item $srcFile $portablePath -Force
        Write-Host "      ✓ $file" -ForegroundColor Green
    }
}

# Si existe config.json, copiarlo también
$configJson = Join-Path $sourcePath "config.json"
if (Test-Path $configJson) {
    Copy-Item $configJson $portablePath -Force
    Write-Host "      ✓ config.json" -ForegroundColor Green
}
Write-Host ""

# Copiar carpetas necesarias
Write-Host "[4/6] Copiando carpetas..." -ForegroundColor Yellow

# Copiar UI
$uiSrc = Join-Path $sourcePath "ui"
if (Test-Path $uiSrc) {
    Copy-Item $uiSrc $portablePath -Recurse -Force
    Write-Host "      ✓ ui\" -ForegroundColor Green
}

# Copiar dependencies (WinFsp)
$depSrc = Join-Path $sourcePath "dependencies"
if (Test-Path $depSrc) {
    Copy-Item $depSrc $portablePath -Recurse -Force
    $winfspMsi = Get-ChildItem "$portablePath\dependencies" -Filter "winfsp*.msi" -ErrorAction SilentlyContinue
    if ($winfspMsi) {
        $sizeMB = [math]::Round($winfspMsi[0].Length / 1MB, 2)
        Write-Host "      ✓ dependencies\ (WinFsp $sizeMB MB)" -ForegroundColor Green
    } else {
        Write-Host "      ✓ dependencies\" -ForegroundColor Green
    }
}

# Copiar Rclone
$rcloneDirs = Get-ChildItem $sourcePath -Directory | Where-Object { $_.Name -like "rclone*" }
if ($rcloneDirs.Count -gt 0) {
    Copy-Item $rcloneDirs[0].FullName $portablePath -Recurse -Force
    Write-Host "      ✓ $($rcloneDirs[0].Name)\" -ForegroundColor Green
}
Write-Host ""

# Crear documentación portable
Write-Host "[5/6] Creando documentación para usuarios..." -ForegroundColor Yellow

$readmePortable = @"
# VultrDrive Desktop - Versión Portable

## 🚀 Inicio Rápido

1. **Ejecuta**: ejecutar_app.bat
2. Si aparece UAC (Control de Cuentas), haz clic en "Sí"
3. WinFsp se instalará automáticamente (solo la primera vez)
4. ¡Listo para usar!

## ✨ Características

- ✅ 100% Portable - Funciona desde cualquier ubicación
- ✅ Sin instalación previa necesaria
- ✅ WinFsp se instala automáticamente
- ✅ Incluye todo lo necesario
- ✅ Funciona sin internet

## 📋 Requisitos

- Windows 10/11 (64-bit)
- Permisos de administrador (solo para instalar WinFsp la primera vez)

## 📂 Contenido

- app.py + módulos → Código del programa
- dependencies/ → Instalador de WinFsp (se instala automático)
- rclone-*/ → Rclone portable
- ui/ → Interfaz gráfica
- ejecutar_app.bat → ¡EJECUTA ESTO!

## 🎯 Cómo Usar

### Primera Vez (en PC nueva)
1. Copia esta carpeta a cualquier ubicación (Escritorio, USB, etc.)
2. Ejecuta: ejecutar_app.bat
3. Cuando aparezca UAC, haz clic en "Sí"
4. WinFsp se instala (tarda ~10 segundos)
5. El programa inicia automáticamente

### Siguientes Veces
1. Ejecuta: ejecutar_app.bat
2. ¡Listo! Ya no pide permisos

## 🔧 Configuración

Al abrir el programa:
1. Ve a la pestaña "Avanzado"
2. Ingresa tus credenciales de Vultr S3
3. Guarda la configuración
4. Ve a "Montar Disco" y selecciona una letra
5. Haz clic en "Montar como Unidad"

## 🚨 Solución de Problemas

### "No se pudo instalar WinFsp"
**Solución**: Ejecuta como administrador
- Clic derecho en ejecutar_app.bat
- "Ejecutar como administrador"

### "No se puede montar la unidad"
**Solución**: Verifica que WinFsp esté instalado
- Busca en: C:\Program Files (x86)\WinFsp
- Si no existe, ejecuta: dependencies\winfsp-*.msi manualmente

### Programa no inicia
**Solución**: Instala Python o usa el ejecutable empaquetado
- Descarga Python 3.11+ desde python.org
- O usa la versión empaquetada (.exe)

## 💡 Características Portables

✅ **Funciona desde USB** - Copia a USB y ejecuta desde ahí
✅ **Cualquier ubicación** - Escritorio, Documentos, Red, etc.
✅ **Sin instalación** - Solo copiar y ejecutar
✅ **Todo incluido** - WinFsp, Rclone, todo necesario
✅ **Offline ready** - No necesita internet para instalar

## 🔐 Seguridad

- Credenciales guardadas localmente
- Comunicación HTTPS con Vultr
- WinFsp: Software de código abierto auditado
- Sin telemetría

## 📞 Soporte

¿Problemas? Revisa:
1. Que tengas permisos de administrador
2. Que Windows 10/11 esté actualizado
3. Que WinFsp se haya instalado correctamente

## 📄 Licencia

Ver archivo LICENSE

---

**VultrDrive Desktop** - Sistema de montaje y sincronización Vultr S3
Versión Portable creada: $(Get-Date -Format "dd/MM/yyyy HH:mm")
"@

$readmePortable | Out-File (Join-Path $portablePath "README.txt") -Encoding UTF8
Write-Host "      ✓ README.txt" -ForegroundColor Green

# Copiar LEEME_PRIMERO.txt si existe
$leemeSrc = Join-Path $sourcePath "LEEME_PRIMERO.txt"
if (Test-Path $leemeSrc) {
    Copy-Item $leemeSrc $portablePath -Force
    Write-Host "      ✓ LEEME_PRIMERO.txt" -ForegroundColor Green
}
Write-Host ""

# Verificar componentes críticos
Write-Host "[6/6] Verificando componentes..." -ForegroundColor Yellow
$errors = 0

if (-not (Test-Path (Join-Path $portablePath "app.py"))) {
    Write-Host "      ✗ app.py falta" -ForegroundColor Red
    $errors++
} else {
    Write-Host "      ✓ app.py" -ForegroundColor Green
}

if (-not (Test-Path (Join-Path $portablePath "ejecutar_app.bat"))) {
    Write-Host "      ✗ ejecutar_app.bat falta" -ForegroundColor Red
    $errors++
} else {
    Write-Host "      ✓ ejecutar_app.bat" -ForegroundColor Green
}

if (-not (Test-Path (Join-Path $portablePath "ui\main_window.py"))) {
    Write-Host "      ✗ ui\main_window.py falta" -ForegroundColor Red
    $errors++
} else {
    Write-Host "      ✓ ui\" -ForegroundColor Green
}

$winfspCheck = Get-ChildItem (Join-Path $portablePath "dependencies") -Filter "winfsp*.msi" -ErrorAction SilentlyContinue
if (-not $winfspCheck) {
    Write-Host "      ✗ WinFsp MSI falta" -ForegroundColor Red
    $errors++
} else {
    Write-Host "      ✓ WinFsp MSI" -ForegroundColor Green
}

$rcloneCheck = Get-ChildItem $portablePath -Recurse -Filter "rclone.exe" -ErrorAction SilentlyContinue
if (-not $rcloneCheck) {
    Write-Host "      ✗ rclone.exe falta" -ForegroundColor Red
    $errors++
} else {
    Write-Host "      ✓ rclone.exe" -ForegroundColor Green
}
Write-Host ""

# Calcular estadísticas
$totalSize = (Get-ChildItem $portablePath -Recurse -File | Measure-Object -Property Length -Sum).Sum / 1MB
$fileCount = (Get-ChildItem $portablePath -Recurse -File).Count

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "           VERSIÓN PORTABLE CREADA" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Ubicación:" -ForegroundColor White
Write-Host "  $portablePath" -ForegroundColor Green
Write-Host ""
Write-Host "  Tamaño: $([math]::Round($totalSize, 2)) MB" -ForegroundColor White
Write-Host "  Archivos: $fileCount" -ForegroundColor White
Write-Host ""

if ($errors -eq 0) {
    Write-Host "  ✅ TODO LISTO - Versión portable completa" -ForegroundColor Green
    Write-Host ""
    Write-Host "  Puedes copiar esta carpeta a:" -ForegroundColor Gray
    Write-Host "    • Otro PC Windows" -ForegroundColor Gray
    Write-Host "    • Memoria USB" -ForegroundColor Gray
    Write-Host "    • Servidor de archivos" -ForegroundColor Gray
    Write-Host "    • Cualquier ubicación" -ForegroundColor Gray
    Write-Host ""
    Write-Host "  Para usar:" -ForegroundColor Gray
    Write-Host "    1. Copia la carpeta al destino" -ForegroundColor Gray
    Write-Host "    2. Ejecuta: ejecutar_app.bat" -ForegroundColor Gray
    Write-Host "    3. ¡Listo!" -ForegroundColor Gray
} else {
    Write-Host "  ⚠️ ADVERTENCIA - Faltan $errors componentes" -ForegroundColor Yellow
    Write-Host "  La versión portable puede no funcionar correctamente" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Abrir carpeta en explorador
Start-Process explorer.exe -ArgumentList $portablePath

