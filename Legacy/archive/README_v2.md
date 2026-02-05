# 🚀 VultrDriveDesktop v2.0

**Una aplicación de escritorio moderna y multiidioma para gestionar tu almacenamiento en la nube Vultr Object Storage.**

## ✨ Nuevas Características v2.0

### 🌐 **Soporte Multiidioma**
- **Español** 🇪🇸 - Interfaz completamente traducida
- **English** 🇺🇸 - Idioma por defecto
- **Français** 🇫🇷 - Soporte completo en francés

### 🎨 **Sistema de Temas**
- **Tema Oscuro** 🌙 - Perfecto para trabajo nocturno
- **Tema Claro** ☀️ - Ideal para uso diurno
- **Cambio instantáneo** - Sin necesidad de reiniciar

### 🔧 **Montaje Mejorado**
- **Detección automática** de rclone
- **Verificación real** del montaje
- **Manejo robusto** de errores
- **Opciones optimizadas** para Windows

## 🎯 Características Principales

### 📁 **Gestión de Archivos**
- Subida de archivos individuales
- Respaldo completo de carpetas
- Navegación intuitiva de buckets
- Formateo seguro de buckets

### ⚡ **Sincronización en Tiempo Real**
- Monitoreo automático de carpetas
- Subida automática de cambios
- Log de actividad en tiempo real
- Control de inicio/parada

### 🔗 **Montaje como Unidad**
- Acceso directo desde "Este Equipo"
- Navegación como disco local
- Copia/pega nativo de Windows
- Selección de letra de unidad

### ⚙️ **Gestión de Perfiles**
- Múltiples configuraciones de almacenamiento
- Cambio rápido entre perfiles
- Configuración segura de credenciales
- Persistencia de configuraciones

## 📋 Requisitos del Sistema

- **Sistema Operativo**: Windows 10/11
- **Python**: 3.8 o superior
- **Memoria RAM**: 4GB mínimo
- **Espacio en disco**: 100MB para la aplicación

## 🚀 Instalación Rápida

### Opción 1: Instalación Automática (Recomendada)
```powershell
# Descargar y ejecutar el instalador
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
.\install.ps1
```

### Opción 2: Instalación Manual
1. **Instalar Python** desde [python.org](https://python.org)
2. **Instalar dependencias**:
   ```bash
   pip install PyQt6 boto3 watchdog
   ```
3. **Descargar rclone** desde [rclone.org](https://rclone.org) (opcional para montaje)
4. **Ejecutar la aplicación**:
   ```powershell
   python app.py
   ```

## 🎮 Guía de Uso

### Primer Uso
1. **Ejecutar la aplicación** (doble clic en acceso directo o `.\start.ps1`)
2. **Configurar un perfil** - Click en "⚙️ Administrar Perfiles"
3. **Añadir credenciales** de tu Vultr Object Storage:
   - Access Key
   - Secret Key
   - Host Base (ej: ewr1.vultrobjects.com)
4. **Seleccionar el perfil** en el menú principal

### Cambiar Idioma
1. Click en el botón **🌐** (esquina superior izquierda)
2. Seleccionar idioma del menú desplegable
3. Reiniciar la aplicación si se solicita

### Cambiar Tema
1. Click en el botón **🎨** (esquina superior derecha)
2. El tema cambia inmediatamente
3. La preferencia se guarda automáticamente

### Subir Archivos
1. **Seleccionar bucket** en la pestaña "Principal"
2. Click en **"📁 Subir Archivo"**
3. Elegir archivo desde el explorador
4. Monitorear progreso en la barra inferior

### Montar como Unidad
1. Ir a la pestaña **"Montar Disco"**
2. **Seleccionar letra** de unidad (V-Z)
3. Click en **"🔗 Montar Unidad"**
4. Acceder desde "Este Equipo" cuando esté listo

### Sincronización Automática
1. Ir a la pestaña **"Sincronización en Tiempo Real"**
2. **Seleccionar carpeta** a monitorear
3. Click en **"▶️ Iniciar Sincronización"**
4. Los cambios se suben automáticamente

## 🛠️ Solución de Problemas

### Error: "Python no encontrado"
```bash
# Instalar Python desde Microsoft Store o python.org
winget install Python.Python.3.11
```

### Error: "Módulo PyQt6 no encontrado"
```bash
pip install PyQt6
```

### Error: "No se puede montar la unidad"
1. Verificar que rclone esté instalado
2. Ejecutar como administrador
3. Verificar credenciales del perfil

### Error: "No se pueden listar buckets"
1. Verificar conexión a internet
2. Comprobar credenciales en configuración
3. Verificar el host base (región correcta)

## 📁 Estructura del Proyecto

```
VultrDriveDesktop/
├── 📄 app.py                 # Aplicación principal
├── 🌐 translations.py        # Sistema de idiomas
├── 🎨 theme_manager.py       # Gestión de temas
├── 📁 ui/
│   ├── main_window.py        # Ventana principal
│   └── settings_window.py    # Ventana de configuración
├── ⚙️ config_manager.py      # Gestión de perfiles
├── ☁️ s3_handler.py          # Cliente Vultr Object Storage
├── 🔗 rclone_manager.py      # Montaje de unidades
├── 👁️ file_watcher.py        # Sincronización tiempo real
├── 📋 requirements.txt       # Dependencias Python
├── 🚀 install.ps1           # Instalador automático
├── ▶️ start.ps1             # Iniciador simple
└── 📖 README.md             # Este archivo
```

## 🔧 Configuración Avanzada

### Archivo de Preferencias
La aplicación crea automáticamente `user_preferences.json`:
```json
{
  "language": "es",
  "theme": "dark"
}
```

### Variables de Entorno
- `VULTR_ACCESS_KEY` - Access Key por defecto
- `VULTR_SECRET_KEY` - Secret Key por defecto
- `VULTR_HOST` - Host base por defecto

### Configuración de rclone
El archivo se crea automáticamente en `~/.config/rclone/rclone.conf`

## 🤝 Contribuir

### Reportar Problemas
1. Abrir un issue en el repositorio
2. Incluir información del sistema
3. Describir pasos para reproducir
4. Adjuntar logs si es posible

### Añadir Idiomas
1. Editar `translations.py`
2. Añadir nuevo diccionario de idioma
3. Actualizar `get_available_languages()`
4. Probar todas las funcionalidades

### Mejoras de Código
1. Fork del repositorio
2. Crear rama para la característica
3. Hacer commit con mensajes descriptivos
4. Crear pull request

## 📝 Historial de Versiones

### v2.0 (06/11/2025)
- ✅ Sistema multiidioma (ES, EN, FR)
- ✅ Temas claro y oscuro
- ✅ Montaje mejorado con verificación
- ✅ Persistencia de preferencias
- ✅ Interfaz reorganizada
- ✅ Instalador automático

### v1.0 (Anterior)
- ✅ Funcionalidad básica de subida/descarga
- ✅ Gestión de perfiles
- ✅ Sincronización en tiempo real
- ✅ Montaje básico de unidades

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver archivo `LICENSE` para más detalles.

## 📞 Soporte

### Documentación
- [Guía Completa](./MEJORAS_IMPLEMENTADAS.md)
- [Solución de Problemas](./TROUBLESHOOTING.md)

### Contacto
- **Issues**: GitHub Issues
- **Email**: Contacto a través del repositorio
- **Wiki**: Documentación extendida en el wiki

---

## 🎉 ¡Gracias por usar VultrDriveDesktop!

**Desarrollado con ❤️ por GitHub Copilot Assistant**

*Si te gusta el proyecto, ¡no olvides darle una ⭐ en GitHub!*