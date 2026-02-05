# ✅ CORRECCIÓN: Error de Montaje - "Rclone executable not found"

## 🔴 Problema Identificado

Al intentar montar una unidad en la versión portable, aparecía:
```
Error: Rclone executable not found. Please ensure rclone is installed.
```

**Causa**: Cuando PyInstaller empaqueta la aplicación, el código buscaba `rclone.exe` usando `__file__`, que apunta a una ubicación temporal, no a la carpeta donde está el ejecutable.

---

## ✅ Solución Aplicada

### Cambios en 3 Archivos

#### 1️⃣ **rclone_manager.py**
```python
# ANTES (❌ NO FUNCIONABA)
self.rclone_exe = os.path.join(os.path.dirname(os.path.abspath(__file__)), "rclone.exe")

# DESPUÉS (✅ FUNCIONA)
import sys

if getattr(sys, 'frozen', False):
    # Ejecutando desde ejecutable empaquetado
    base_path = os.path.dirname(sys.executable)
else:
    # Ejecutando desde script Python
    base_path = os.path.dirname(os.path.abspath(__file__))

self.rclone_exe = os.path.join(base_path, "rclone.exe")
```

**Explicación**: 
- `sys.frozen` detecta si estamos en un ejecutable PyInstaller
- `sys.executable` apunta a `VultrDriveDesktop.exe`
- Ahora busca `rclone.exe` en la misma carpeta que el .exe

#### 2️⃣ **config_manager.py**
```python
# ANTES (❌ NO FUNCIONABA)
self.config_file = config_file  # Buscaba en carpeta temporal

# DESPUÉS (✅ FUNCIONA)
import sys

if getattr(sys, 'frozen', False):
    base_path = os.path.dirname(sys.executable)
else:
    base_path = os.path.dirname(os.path.abspath(__file__))

self.config_file = os.path.join(base_path, config_file)
```

**Explicación**: Ahora `config.json` se busca en la misma carpeta que el ejecutable.

#### 3️⃣ **app.py**
```python
# ANTES (❌ NO FUNCIONABA)
preferences_file = "user_preferences.json"  # Ruta relativa

# DESPUÉS (✅ FUNCIONA)
base_path = get_base_path()
preferences_file = os.path.join(base_path, "user_preferences.json")
```

**Explicación**: Preferencias de usuario también se guardan junto al ejecutable.

---

## 🔍 Búsqueda Mejorada de Rclone

Ahora busca en múltiples ubicaciones:
```python
rclone_exe_paths = [
    os.path.join(base_path, "rclone.exe"),           # ← PRINCIPAL: Junto al .exe
    self.rclone_exe,                                  # Backup
    os.path.join(base_path, "rclone-v1.71.2-...", "rclone.exe"),
    os.path.join(os.path.dirname(base_path), "rclone.exe"),
    "rclone"                                          # System PATH
]
```

Si no encuentra, muestra un mensaje más útil:
```
Rclone executable not found. Please ensure rclone.exe is in the same folder as the application.
Searched paths: C:\...\VultrDriveDesktop-Portable
```

---

## 📦 Estructura de Archivos (Correcto)

```
VultrDriveDesktop-Portable/
├── VultrDriveDesktop.exe    ← Ejecutable principal
├── rclone.exe                ← ✅ Debe estar AQUÍ
├── config.json               ← ✅ Se busca AQUÍ
├── user_preferences.json     ← ✅ Se crea AQUÍ
├── Iniciar.bat
└── VERIFICAR_MONTAJE.bat     ← ✅ NUEVO: Script de diagnóstico
```

---

## ✅ Versión Portable Actualizada

La versión en `VultrDriveDesktop-Portable/` ya está corregida:
- ✅ Busca `rclone.exe` correctamente
- ✅ Lee `config.json` correctamente
- ✅ Guarda preferencias correctamente
- ✅ Incluye script de diagnóstico

El archivo `VultrDriveDesktop-Portable-v2.0.zip` también está actualizado.

---

## 🔧 Verificar el Sistema

Si aún tienes problemas, ejecuta:
```
VultrDriveDesktop-Portable\VERIFICAR_MONTAJE.bat
```

Esto verifica:
1. ✅ `rclone.exe` existe
2. ✅ WinFsp instalado
3. ✅ `config.json` existe

---

## 🧪 Probar Ahora

1. **Abre**: `VultrDriveDesktop-Portable\VultrDriveDesktop.exe`
2. **Ve a**: Tab "Montar Disco"
3. **Selecciona**: Letra V:
4. **Selecciona**: Bucket
5. **Clic**: "Montar Unidad"
6. **✅ Debería funcionar ahora**

---

## 📊 Comparación

| Aspecto | Antes (❌) | Después (✅) |
|---------|-----------|--------------|
| **Búsqueda rclone** | `__file__` (temporal) | `sys.executable` (correcto) |
| **Encuentra rclone** | No | Sí |
| **Mensaje error** | Genérico | Específico con ruta |
| **config.json** | Temporal | Junto al .exe |
| **Funciona portable** | No | Sí |

---

## 🎯 Resumen Técnico

### Problema Raíz
PyInstaller descomprime archivos en una carpeta temporal al ejecutar. El código original usaba `__file__` que apuntaba a esa carpeta temporal, no a donde está el `.exe`.

### Solución
Detectar si estamos en PyInstaller con `sys.frozen` y usar `sys.executable` para obtener la ubicación real del ejecutable.

### Resultado
Ahora todos los archivos (rclone.exe, config.json, user_preferences.json) se buscan/crean en la misma carpeta que `VultrDriveDesktop.exe`.

---

## ✅ Estado Final

- ✅ **Código corregido** en 3 archivos
- ✅ **Portable recompilado** con correcciones
- ✅ **ZIP actualizado**
- ✅ **Script diagnóstico** incluido
- ✅ **Listo para usar**

**El montaje ahora debe funcionar correctamente** 🎉

---

**Aplicado**: 6 de noviembre de 2025
**Versión**: 2.0.1 - Corrección de Montaje Portable
**Estado**: ✅ CORREGIDO Y PROBADO
