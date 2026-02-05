# 🔧 Solución: Error al Montar como Disco

## 🔴 Problema
```
Mount failed: 2025/11/06 02:13:37 CRITICAL: Fatal error: daemon mode is not supported on the windows platform
```

## ✅ Solución

El error tiene **DOS causas**:

### 1. **WinFsp no está instalado** (Principal)
WinFsp es un software **requerido** para montar unidades virtuales en Windows, similar a FUSE en Linux.

### 2. **Flags incompatibles con Windows**
Las banderas `--daemon` y `--network-mode` no son soportadas en Windows.

---

## 📥 Instalación de WinFsp

### Opción 1: Instalación Automática (Recomendada)
```powershell
.\instalar_winfsp.ps1
```

### Opción 2: Instalación Manual
1. Descarga WinFsp desde: https://winfsp.dev/rel/
2. Descarga el archivo: `winfsp-2.0.23075.msi` (o versión más reciente)
3. Ejecuta el instalador MSI
4. Sigue el asistente de instalación
5. Reinicia la aplicación VultrDriveDesktop

---

## 🔍 Verificar Instalación

Para verificar que WinFsp está instalado correctamente:

```powershell
.\verificar_winfsp.ps1
```

Debería mostrar:
```
✓ OK - WinFsp instalado
```

---

## 🎯 Después de Instalar WinFsp

1. **Cierra** la aplicación VultrDriveDesktop si está abierta
2. **Abre** nuevamente la aplicación
3. Ve a la pestaña **"Montar Disco"**
4. Selecciona una **Letra de Unidad** (ejemplo: W:)
5. Haz clic en **"Montar Unidad"**

Ahora debería funcionar correctamente ✅

---

## 📝 Correcciones Aplicadas al Código

### Archivo: `rclone_manager.py`

**ANTES** (con errores):
```python
cmd = [
    rclone_path,
    "mount",
    remote_path,
    mount_point,
    "--network-mode",  # ❌ No soportado en Windows
    "--daemon"         # ❌ No soportado en Windows
]
```

**DESPUÉS** (corregido):
```python
cmd = [
    rclone_path,
    "mount",
    remote_path,
    mount_point,
    "--vfs-cache-mode", "writes",
    "--vfs-cache-max-age", "1h",
    "--volname", f"Vultr-{profile_name}"
]

# Proceso en segundo plano con CREATE_NEW_PROCESS_GROUP
self.mount_process = subprocess.Popen(
    cmd,
    creationflags=subprocess.CREATE_NO_WINDOW | subprocess.CREATE_NEW_PROCESS_GROUP
)
```

---

## ❓ Preguntas Frecuentes

### ¿Por qué necesito WinFsp?
Windows no tiene soporte nativo para sistemas de archivos virtuales como Linux (FUSE). WinFsp proporciona esta funcionalidad.

### ¿Es seguro WinFsp?
Sí, es un proyecto de código abierto mantenido activamente. Es usado por muchas aplicaciones populares como Google Drive File Stream, OneDrive, etc.

### ¿Afecta al rendimiento?
No, WinFsp está altamente optimizado y tiene un impacto mínimo en el rendimiento.

### ¿Qué pasa si no instalo WinFsp?
No podrás usar la función de "Montar como Disco", pero el resto de la aplicación (subir archivos, sincronización, backup) funcionará normalmente.

---

## 🚀 Scripts Disponibles

| Script | Propósito |
|--------|-----------|
| `instalar_winfsp.ps1` | Descarga e instala WinFsp automáticamente |
| `verificar_winfsp.ps1` | Verifica si WinFsp está instalado |
| `start.bat` / `start.ps1` | Inicia la aplicación |

---

## 📞 Soporte

Si después de instalar WinFsp sigues teniendo problemas:

1. **Reinicia tu computadora** (asegura que los drivers se carguen)
2. Ejecuta `verificar_winfsp.ps1` para confirmar la instalación
3. Revisa que tienes permisos de administrador
4. Verifica que el antivirus no esté bloqueando WinFsp

---

**Última actualización**: 6 de noviembre de 2025
