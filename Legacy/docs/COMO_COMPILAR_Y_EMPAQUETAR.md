# 📦 GUÍA: Cómo Compilar y Empaquetar VultrDriveDesktop

## 🎯 Objetivo

Aprender a **compilar y crear el ZIP portable** tú mismo sin necesidad de ayuda.

---

## 📋 Requisitos Previos

1. ✅ **Python 3.14.0** instalado
2. ✅ **PyInstaller** instalado (`pip install pyinstaller`)
3. ✅ Todas las dependencias instaladas (`pip install -r requirements.txt`)

Para verificar:
```powershell
python --version     # Debe mostrar: Python 3.14.0
pip list | Select-String pyinstaller  # Debe aparecer
```

---

## 🚀 MÉTODO 1: Automático con EMPAQUETAR.bat (RECOMENDADO)

### Paso 1: Ejecutar el Script Automático

```powershell
.\EMPAQUETAR.bat
```

**¿Qué hace este script?**
1. ✅ Verifica que Python esté instalado
2. ✅ Instala PyInstaller si no está
3. ✅ Crea la carpeta `VultrDriveDesktop-Portable`
4. ✅ Compila `app.py` a `.exe` (tarda 2-5 minutos)
5. ✅ Copia todos los archivos necesarios:
   - `VultrDriveDesktop.exe` (compilado)
   - `rclone.exe`
   - `config.json`
   - `user_preferences.json`
   - Documentación (README, GUÍA VISUAL, etc.)
   - `INSTALAR_WINFSP.bat`
6. ✅ Limpia archivos temporales

**Salida:**
```
=== COMPILACION EXITOSA ===
Tamano total: 170.15 MB
```

### Paso 2: Crear el ZIP

```powershell
# Eliminar ZIP antiguo (si existe)
if (Test-Path "VultrDriveDesktop-Portable.zip") { 
    Remove-Item "VultrDriveDesktop-Portable.zip" -Force 
}

# Crear nuevo ZIP
Compress-Archive -Path "VultrDriveDesktop-Portable\*" `
                 -DestinationPath "VultrDriveDesktop-Portable.zip" `
                 -Force

# Verificar
Get-Item "VultrDriveDesktop-Portable.zip" | Select-Object Name, @{Name="Tamaño (MB)";Expression={[math]::Round($_.Length/1MB,2)}}
```

**Salida:**
```
Name                           Tamaño (MB)
----                           -----------
VultrDriveDesktop-Portable.zip      125.38
```

### ✅ ¡LISTO! Ya tienes tu portable actualizado.

---

## 🛠️ MÉTODO 2: Manual Paso a Paso

### Paso 1: Compilar con PyInstaller

```powershell
# Eliminar build anterior (opcional)
if (Test-Path "build") { Remove-Item "build" -Recurse -Force }
if (Test-Path "dist") { Remove-Item "dist" -Recurse -Force }

# Compilar
pyinstaller --onefile `
            --windowed `
            --icon=icon.ico `
            --add-data "splash_screen.py;." `
            --name VultrDriveDesktop `
            app.py
```

**Explicación de parámetros:**
- `--onefile`: Un solo .exe (no carpeta con DLLs)
- `--windowed`: Sin consola negra de fondo
- `--icon=icon.ico`: Icono de la aplicación
- `--add-data`: Incluir splash_screen.py
- `--name`: Nombre del .exe

**Tiempo:** 2-5 minutos

**Resultado:** `dist\VultrDriveDesktop.exe` (~104 MB)

### Paso 2: Crear Carpeta Portable

```powershell
# Crear carpeta
if (Test-Path "VultrDriveDesktop-Portable") { 
    Remove-Item "VultrDriveDesktop-Portable" -Recurse -Force 
}
New-Item -ItemType Directory -Path "VultrDriveDesktop-Portable" -Force
```

### Paso 3: Copiar Archivos

```powershell
# Copiar ejecutable compilado
Copy-Item "dist\VultrDriveDesktop.exe" "VultrDriveDesktop-Portable\"

# Copiar rclone
Copy-Item "rclone-v1.71.2-windows-amd64\rclone.exe" "VultrDriveDesktop-Portable\"

# Copiar configuraciones
Copy-Item "config.example.json" "VultrDriveDesktop-Portable\config.json"
Copy-Item "user_preferences.json" "VultrDriveDesktop-Portable\"

# Copiar documentación
Copy-Item "README.md" "VultrDriveDesktop-Portable\README_COMPLETO.md"
Copy-Item "QUICK_START.md" "VultrDriveDesktop-Portable\"
Copy-Item "GUIA_VISUAL.md" "VultrDriveDesktop-Portable\"
Copy-Item "SOLUCION_MONTAJE.md" "VultrDriveDesktop-Portable\"

# Copiar instalador de WinFsp
Copy-Item "winfsp-*.msi" "VultrDriveDesktop-Portable\INSTALAR_WINFSP.bat"
```

### Paso 4: Crear README.txt

```powershell
@"
================================
   VultrDriveDesktop Portable
================================

VERSION PORTABLE - No requiere instalaciÃ³n de Python

IDIOMAS DISPONIBLES:
  🇲🇽 EspaÃ±ol (MÃ©xico) - DEFAULT
  🇺🇸 English (USA)
  🇫🇷 FranÃ§ais (France)
  🇩🇪 Deutsch (Deutschland)
  🇧🇷 PortuguÃªs (Brasil)

INICIO RAPIDO:
  1. Instala WinFsp (si quieres montar unidades):
     - Ejecuta INSTALAR_WINFSP.bat
  
  2. Ejecuta VultrDriveDesktop.exe
  
  3. Configura tu cuenta Vultr:
     - API Key
     - Selecciona tu bucket

CONTENIDO:
  - VultrDriveDesktop.exe    : Aplicacion principal
  - rclone.exe               : Motor de sincronizacion
  - config.json              : Configuracion de perfiles
  - user_preferences.json    : Preferencias (idioma, tema)
  - INSTALAR_WINFSP.bat      : Instalador de WinFsp
  - README_COMPLETO.md       : DocumentaciÃ³n completa
  - QUICK_START.md           : GuÃ­a de inicio rÃ¡pido
  - GUIA_VISUAL.md           : Capturas de pantalla
  - SOLUCION_MONTAJE.md      : Si tienes problemas montando

VENTAJAS:
  [âœ"] No necesita Python instalado
  [âœ"] Tu configuraciÃ³n ya incluida
  [âœ"] Todo autocontenido
  [âœ"] Portable - Lleva a cualquier PC
  [âœ"] 5 idiomas completos
  [âœ"] Splash screen rÃ¡pido (5ms)
  [âœ"] Optimizado para rendimiento

SOPORTE:
  - GitHub: https://github.com/aprendeineamx-max/VultrDriveDesktop
  - Documentacion: Ver README_COMPLETO.md

"@ | Out-File "VultrDriveDesktop-Portable\README.txt" -Encoding UTF8
```

### Paso 5: Crear Iniciar.bat

```powershell
@"
@echo off
echo Iniciando VultrDriveDesktop Portable...
start VultrDriveDesktop.exe
"@ | Out-File "VultrDriveDesktop-Portable\Iniciar.bat" -Encoding UTF8
```

### Paso 6: Crear ZIP

```powershell
# Eliminar ZIP antiguo
if (Test-Path "VultrDriveDesktop-Portable.zip") { 
    Remove-Item "VultrDriveDesktop-Portable.zip" -Force 
}

# Comprimir
Compress-Archive -Path "VultrDriveDesktop-Portable\*" `
                 -DestinationPath "VultrDriveDesktop-Portable.zip" `
                 -Force

# Verificar
Write-Host "`n✅ ZIP CREADO`n" -ForegroundColor Green
Get-Item "VultrDriveDesktop-Portable.zip" | Select-Object Name, @{Name="Tamaño (MB)";Expression={[math]::Round($_.Length/1MB,2)}}
```

---

## 🔄 MÉTODO 3: Script PowerShell Completo (TODO EN UNO)

Guarda este script como **`compilar_y_empaquetar.ps1`**:

```powershell
# ====================================
#  SCRIPT COMPLETO: Compilar y ZIP
# ====================================

Write-Host "`n=== COMPILACION Y EMPAQUETADO ===" -ForegroundColor Cyan

# 1. Compilar
Write-Host "`n1. Compilando con PyInstaller..." -ForegroundColor Yellow
.\EMPAQUETAR.bat

# 2. Crear ZIP
Write-Host "`n2. Creando ZIP..." -ForegroundColor Yellow

if (Test-Path "VultrDriveDesktop-Portable.zip") { 
    Remove-Item "VultrDriveDesktop-Portable.zip" -Force 
}

Compress-Archive -Path "VultrDriveDesktop-Portable\*" `
                 -DestinationPath "VultrDriveDesktop-Portable.zip" `
                 -Force

# 3. Verificar
Write-Host "`n=== RESULTADOS ===" -ForegroundColor Green

Write-Host "`nCarpeta Portable:" -ForegroundColor Yellow
Get-ChildItem "VultrDriveDesktop-Portable" | 
    Select-Object Name, @{Name="Tamaño (MB)";Expression={[math]::Round($_.Length/1MB,2)}} | 
    Format-Table -AutoSize

Write-Host "`nArchivo ZIP:" -ForegroundColor Yellow
Get-Item "VultrDriveDesktop-Portable.zip" | 
    Select-Object Name, @{Name="Tamaño (MB)";Expression={[math]::Round($_.Length/1MB,2)}} | 
    Format-Table -AutoSize

Write-Host "`n✅ PROCESO COMPLETADO`n" -ForegroundColor Green
```

**Ejecutar:**
```powershell
.\compilar_y_empaquetar.ps1
```

---

## ⚡ COMANDOS RÁPIDOS (Un Solo Comando)

### Compilar + ZIP en una línea:

```powershell
.\EMPAQUETAR.bat; if (Test-Path "VultrDriveDesktop-Portable.zip") { Remove-Item "VultrDriveDesktop-Portable.zip" -Force }; Compress-Archive -Path "VultrDriveDesktop-Portable\*" -DestinationPath "VultrDriveDesktop-Portable.zip" -Force; Write-Host "`n✅ LISTO`n" -ForegroundColor Green; Get-Item "VultrDriveDesktop-Portable.zip" | Select-Object Name, @{Name="Tamaño (MB)";Expression={[math]::Round($_.Length/1MB,2)}}
```

---

## 🔍 Verificar que Todo Está Actualizado

### Ver fechas de archivos:

```powershell
Get-ChildItem "VultrDriveDesktop-Portable" | 
    Select-Object Name, LastWriteTime, @{Name="Tamaño (MB)";Expression={[math]::Round($_.Length/1MB,2)}} | 
    Format-Table -AutoSize
```

**Verifica que `VultrDriveDesktop.exe` tenga la fecha/hora reciente.**

### Ver contenido del ZIP:

```powershell
Add-Type -AssemblyName System.IO.Compression.FileSystem
$zip = [System.IO.Compression.ZipFile]::OpenRead("$PWD\VultrDriveDesktop-Portable.zip")
$zip.Entries | Select-Object FullName, Length, LastWriteTime | Format-Table -AutoSize
$zip.Dispose()
```

---

## 🐛 Solución de Problemas

### Problema: "PyInstaller no encontrado"

**Solución:**
```powershell
pip install pyinstaller
```

### Problema: "Error al compilar"

**Solución:**
```powershell
# Limpiar cache
if (Test-Path "build") { Remove-Item "build" -Recurse -Force }
if (Test-Path "dist") { Remove-Item "dist" -Recurse -Force }
if (Test-Path "__pycache__") { Remove-Item "__pycache__" -Recurse -Force }

# Volver a compilar
.\EMPAQUETAR.bat
```

### Problema: "Archivos con fechas antiguas"

**Solución:**
```powershell
# Eliminar carpeta portable anterior
Remove-Item "VultrDriveDesktop-Portable" -Recurse -Force

# Volver a compilar desde cero
.\EMPAQUETAR.bat
```

### Problema: "ZIP muy grande"

**Verifica:**
- El .exe es ~104 MB (normal con PyQt6)
- rclone.exe es ~66 MB
- Total carpeta: ~170 MB
- ZIP comprimido: ~125 MB

**Esto es normal para una app PyQt6 empaquetada.**

---

## 📝 Resumen de Archivos Importantes

### En la carpeta raíz:

| Archivo | Descripción |
|---------|-------------|
| `app.py` | Código fuente principal |
| `translations.py` | Sistema de traducciones (5 idiomas) |
| `splash_screen.py` | Pantalla de inicio |
| `EMPAQUETAR.bat` | Script de compilación automático |
| `requirements.txt` | Dependencias Python |

### En VultrDriveDesktop-Portable:

| Archivo | Descripción | Tamaño |
|---------|-------------|--------|
| `VultrDriveDesktop.exe` | Aplicación compilada | ~104 MB |
| `rclone.exe` | Motor de sincronización | ~66 MB |
| `config.json` | Configuración de perfiles | <1 KB |
| `user_preferences.json` | Idioma y tema | <1 KB |
| `README.txt` | Guía rápida portable | <1 KB |
| `Iniciar.bat` | Atajo de inicio | <1 KB |
| `INSTALAR_WINFSP.bat` | Instalador WinFsp | ~4 KB |

---

## 🎓 PROCESO COMPLETO PASO A PASO (Resumen)

### 🟢 Opción Simple (RECOMENDADO):

```powershell
# 1. Compilar
.\EMPAQUETAR.bat

# 2. Crear ZIP
Compress-Archive -Path "VultrDriveDesktop-Portable\*" -DestinationPath "VultrDriveDesktop-Portable.zip" -Force

# 3. Verificar
Get-Item "VultrDriveDesktop-Portable.zip"
```

### 🟡 Opción Intermedia:

```powershell
# Un solo comando hace todo
.\EMPAQUETAR.bat; Compress-Archive -Path "VultrDriveDesktop-Portable\*" -DestinationPath "VultrDriveDesktop-Portable.zip" -Force
```

### 🔴 Opción Manual (Completa):

1. Compilar: `pyinstaller --onefile --windowed --add-data "splash_screen.py;." app.py`
2. Crear carpeta: `New-Item -ItemType Directory -Path "VultrDriveDesktop-Portable"`
3. Copiar archivos: `.exe`, `rclone.exe`, configs, docs
4. Crear ZIP: `Compress-Archive`

---

## ✅ Checklist Final

Antes de distribuir, verifica:

- [ ] `VultrDriveDesktop.exe` tiene fecha/hora reciente
- [ ] Carpeta portable contiene 11 archivos
- [ ] ZIP pesa ~125 MB
- [ ] Al descomprimir, todos los archivos están
- [ ] Doble clic en .exe abre la app correctamente
- [ ] Idioma default es Español 🇲🇽
- [ ] Todas las traducciones funcionan

---

## 🚀 TIP PRO: Automatización Total

Crea un alias en tu PowerShell profile:

```powershell
# Abrir perfil
notepad $PROFILE

# Agregar función
function Build-VultrPortable {
    Set-Location "C:\Users\lvarg\Desktop\VultrDriveDesktop"
    .\EMPAQUETAR.bat
    if (Test-Path "VultrDriveDesktop-Portable.zip") { 
        Remove-Item "VultrDriveDesktop-Portable.zip" -Force 
    }
    Compress-Archive -Path "VultrDriveDesktop-Portable\*" `
                     -DestinationPath "VultrDriveDesktop-Portable.zip" `
                     -Force
    Write-Host "`n✅ BUILD COMPLETADO`n" -ForegroundColor Green
    Get-Item "VultrDriveDesktop-Portable.zip"
}
```

**Uso:**
```powershell
Build-VultrPortable
```

¡Un solo comando desde cualquier lugar! 🎉

---

**Última actualización:** 06/11/2025 04:42 a.m.
**Versión:** 2.0 con Traducciones Completas
**Tiempo total:** ~3-5 minutos
