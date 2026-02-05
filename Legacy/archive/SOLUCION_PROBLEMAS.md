# 🔧 Solución de Problemas - VultrDriveDesktop

## ❌ Error: "Python no encontrado"

### Síntomas:
```
no se encontró Python
'python' no se reconoce como un comando interno o externo
```

### Soluciones:

#### Opción 1: Instalar desde Microsoft Store (MÁS FÁCIL)
1. Abrir **Microsoft Store**
2. Buscar "**Python 3.11**"
3. Hacer clic en **Instalar**
4. Esperar a que termine
5. Ejecutar nuevamente `setup.ps1`

#### Opción 2: Descarga directa
1. Visitar: https://www.python.org/downloads/
2. Descargar **Python 3.11 o superior**
3. Durante la instalación:
   - ✅ **IMPORTANTE**: Marcar "**Add Python to PATH**"
   - Hacer clic en "Install Now"
4. Reiniciar la terminal
5. Ejecutar nuevamente `setup.ps1`

#### Opción 3: Usar Python Launcher
Si ya tiene Python instalado pero el comando no funciona:
```powershell
# En lugar de:
python app.py

# Use:
py app.py
```

---

## ❌ Error: "Módulo PyQt6 no encontrado"

### Síntomas:
```
ModuleNotFoundError: No module named 'PyQt6'
```

### Solución:
```bash
# Ejecutar el instalador completo
.\setup.ps1

# O instalar manualmente
py -m pip install PyQt6 boto3 watchdog
```

---

## ❌ Error: "No se puede montar la unidad"

### Síntomas:
- La unidad no aparece en "Este Equipo"
- Error: "rclone not found"
- Error: "Mount failed"

### Soluciones:

#### 1. Verificar que rclone esté instalado
```powershell
# Verificar si existe
Test-Path "rclone-v1.65.0-windows-amd64\rclone.exe"
```

#### 2. Descargar rclone manualmente
1. Visitar: https://rclone.org/downloads/
2. Descargar "Windows 64-bit"
3. Extraer en la carpeta de VultrDriveDesktop
4. Reintentar el montaje

#### 3. Ejecutar como Administrador
- Click derecho en `start.bat` → "Ejecutar como administrador"

#### 4. Verificar credenciales
- Ir a "Administrar Perfiles"
- Verificar Access Key, Secret Key y Host Base
- Asegurar que el perfil esté guardado

#### 5. Probar otra letra de unidad
- En lugar de V:, probar con W:, X:, Y: o Z:

---

## ❌ Error: "No se pueden listar buckets"

### Síntomas:
- "No buckets found or error connecting"
- Lista de buckets vacía
- Error de conexión

### Soluciones:

#### 1. Verificar conexión a Internet
```powershell
ping google.com
```

#### 2. Verificar credenciales
- Access Key correcto
- Secret Key correcto
- Host Base correcto (ej: `ewr1.vultrobjects.com`)

#### 3. Verificar región
Regiones comunes de Vultr:
- `ewr1.vultrobjects.com` (Nueva Jersey)
- `sjc1.vultrobjects.com` (Silicon Valley)
- `ams1.vultrobjects.com` (Amsterdam)

#### 4. Probar en consola de Vultr
- Iniciar sesión en https://my.vultr.com
- Verificar que los buckets existan
- Verificar que las credenciales tengan permisos

---

## ❌ Error: "Script de PowerShell no se ejecuta"

### Síntomas:
```
La ejecución de scripts está deshabilitada en este sistema
```

### Solución:
```powershell
# Ejecutar una vez (en PowerShell como Administrador):
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# O ejecutar con bypass temporal:
powershell -ExecutionPolicy Bypass -File .\setup.ps1
```

---

## ❌ Error: "La aplicación no inicia"

### Síntomas:
- Ventana aparece y desaparece
- No hay interfaz gráfica
- Error de importación

### Soluciones:

#### 1. Verificar todas las dependencias
```powershell
py -m pip install --upgrade PyQt6 boto3 watchdog
```

#### 2. Ejecutar desde terminal para ver errores
```powershell
py app.py
```

#### 3. Verificar versión de Python
```powershell
py --version
# Debe ser 3.8 o superior
```

#### 4. Reinstalar PyQt6
```powershell
py -m pip uninstall PyQt6
py -m pip install PyQt6
```

---

## ❌ Error: "Sincronización en tiempo real no funciona"

### Síntomas:
- Los archivos no se suben automáticamente
- El log no muestra actividad

### Soluciones:

#### 1. Verificar que watchdog esté instalado
```powershell
py -m pip install watchdog
```

#### 2. Verificar permisos de carpeta
- Asegurar que tiene permisos de lectura en la carpeta
- Probar con una carpeta diferente

#### 3. Reiniciar sincronización
- Click en "Detener Sincronización"
- Esperar 5 segundos
- Click en "Iniciar Sincronización"

---

## ❌ Error: "Tema o idioma no cambia"

### Síntomas:
- El idioma sigue en inglés
- El tema no cambia

### Soluciones:

#### 1. Reiniciar la aplicación
- Cerrar completamente VultrDriveDesktop
- Abrir nuevamente

#### 2. Verificar archivo de preferencias
```powershell
# Ver contenido
Get-Content user_preferences.json
```

#### 3. Eliminar y recrear preferencias
```powershell
Remove-Item user_preferences.json
# Reiniciar la aplicación
```

---

## 🆘 Obtener Más Ayuda

### Información del Sistema
Ejecutar este comando y copiar la salida:
```powershell
Write-Host "Sistema: $(Get-WmiObject Win32_OperatingSystem | Select-Object -ExpandProperty Caption)"
Write-Host "Python: $(py --version 2>&1)"
Write-Host "PyQt6: $(py -c 'import PyQt6; print(PyQt6.__version__)' 2>&1)"
Write-Host "Rclone: $(if (Test-Path 'rclone-v1.65.0-windows-amd64\rclone.exe') {'Instalado'} else {'No instalado'})"
```

### Logs de Errores
Ejecutar la aplicación desde terminal para ver errores:
```powershell
py app.py
```

### Reportar un Problema
Incluir en el reporte:
- Versión de Windows
- Versión de Python
- Mensaje de error completo
- Pasos para reproducir el problema

---

## ✅ Verificación Rápida

Ejecutar este script para verificar que todo esté bien:

```powershell
Write-Host "=== VERIFICACION RAPIDA ===" -ForegroundColor Cyan
Write-Host ""

# Python
try {
    $pyVer = py --version 2>&1
    Write-Host "Python: OK - $pyVer" -ForegroundColor Green
} catch {
    Write-Host "Python: ERROR - No instalado" -ForegroundColor Red
}

# PyQt6
try {
    py -c "import PyQt6" 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "PyQt6: OK" -ForegroundColor Green
    } else {
        Write-Host "PyQt6: ERROR - No instalado" -ForegroundColor Red
    }
} catch {
    Write-Host "PyQt6: ERROR - No instalado" -ForegroundColor Red
}

# boto3
try {
    py -c "import boto3" 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "boto3: OK" -ForegroundColor Green
    } else {
        Write-Host "boto3: ERROR - No instalado" -ForegroundColor Red
    }
} catch {
    Write-Host "boto3: ERROR - No instalado" -ForegroundColor Red
}

# rclone
if (Test-Path "rclone-v1.65.0-windows-amd64\rclone.exe") {
    Write-Host "rclone: OK" -ForegroundColor Green
} else {
    Write-Host "rclone: AVISO - No instalado (montaje no disponible)" -ForegroundColor Yellow
}

# Archivos
$files = @("app.py", "translations.py", "theme_manager.py", "ui\main_window.py")
$allOk = $true
foreach ($f in $files) {
    if (Test-Path $f) {
        Write-Host "$f : OK" -ForegroundColor Green
    } else {
        Write-Host "$f : ERROR - Faltante" -ForegroundColor Red
        $allOk = $false
    }
}

Write-Host ""
if ($allOk) {
    Write-Host "TODO OK - La aplicacion deberia funcionar" -ForegroundColor Green
} else {
    Write-Host "HAY PROBLEMAS - Revisar errores arriba" -ForegroundColor Red
}
```

Guardar como `verificar.ps1` y ejecutar para diagnóstico rápido.

---

**Última actualización**: 06/11/2025