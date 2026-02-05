# Vultr Drive Desktop 🚀

[![Version](https://img.shields.io/badge/version-2.0-blue.svg)](https://github.com/aprendeineamx-max/VultrDriveDesktop)
[![Python](https://img.shields.io/badge/python-3.9%2B-green.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-orange.svg)](LICENSE)

Una aplicación de escritorio completa y optimizada para gestionar tu almacenamiento en Vultr Object Storage con soporte multiidioma y montaje de disco inteligente.

## 🎯 Novedades v2.0

- **🌍 5 Idiomas Completos**: Español 🇲🇽, English 🇺🇸, Français 🇫🇷, Deutsch 🇩🇪, Português 🇧🇷
- **⚡ Rendimiento Optimizado**: Lazy loading (0.07ms), startup en 500ms
- **🔧 WinFsp Inteligente**: Instalación automática y condicional (solo si no está presente)
- **🧹 Limpieza Automática**: Desmonta unidades colgadas al iniciar
- **🎨 Splash Rediseñado**: Interfaz moderna y profesional
- **🌐 Soporte Multi-Máquina**: Monta el mismo bucket en múltiples VPS simultáneamente
- **💬 Mensajes Detallados**: Errores en español con soluciones paso a paso

## ✨ Características Principales

### 1. **Gestión de Perfiles**
   - Añadir múltiples cuentas de Vultr Object Storage
   - Cambiar entre perfiles fácilmente
   - Editar y eliminar perfiles existentes
   - Configuración segura con encriptación

### 2. **Operaciones de Archivos**
   - Subir archivos individuales con validación
   - Backup completo de carpetas con preservación de estructura
   - Barra de progreso en tiempo real
   - Selección de bucket de destino
   - Soporte para archivos grandes (multipart upload)

### 3. **Montaje de Disco** 🔥
   - Monta tu Object Storage como una unidad de disco en "Este equipo"
   - Elige la letra de unidad que prefieras (V-Z)
   - Accede a tus archivos como si estuvieran en tu PC
   - VFS cache mode para mejor rendimiento
   - Desmontaje seguro automático
   - **NUEVO**: Soporte multi-máquina sin conflictos

### 4. **Opciones Avanzadas**
   - Formatear buckets (con confirmación doble para seguridad)
   - Eliminar todos los archivos de un bucket
   - Gestión de permisos y políticas

### 5. **Multiidioma** 🌍
   - **Español (México)** - Idioma por defecto 🇲🇽
   - **English (USA)** 🇺🇸
   - **Français** 🇫🇷
   - **Deutsch** 🇩🇪
   - **Português (Brasil)** 🇧🇷
   - Cambio de idioma en tiempo real
   - 100% traducido (interfaz + mensajes de error)

### 6. **Backup Rápido desde Escritorio**
   - Acceso directo en el escritorio para backups instantáneos
   - Sin necesidad de abrir la aplicación principal
   - Notificaciones de progreso

## 📦 Instalación

### Opción 1: Version Portable (Recomendada)

1. **Descarga** el archivo `VultrDriveDesktop-Portable.zip` desde [Releases](https://github.com/aprendeineamx-max/VultrDriveDesktop/releases)
2. **Descomprime** en cualquier carpeta
3. **Ejecuta** `VultrDriveDesktop.exe`
4. ¡Listo! No requiere instalación

**Contenido del portable (170MB):**
- ✅ Python incluido
- ✅ Todas las dependencias
- ✅ Rclone preconfigurado
- ✅ WinFsp se instala automáticamente si es necesario
- ✅ Configuración persistente

### Opción 2: Desde el Código Fuente

#### Requisitos Previos
- Windows 10/11 o Windows Server
- Python 3.9 o superior
- Git (opcional)

#### Instalación

```powershell
# Clonar el repositorio
git clone https://github.com/aprendeineamx-max/VultrDriveDesktop.git
cd VultrDriveDesktop

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar la aplicación
python app.py
```

### Dependencias

```txt
PyQt6>=6.6.0
boto3>=1.34.0
watchdog>=4.0.0
pywin32>=306
```

## 🚀 Uso

### Iniciar la Aplicación

**Desde el código fuente:**
```powershell
cd c:\Users\lvarg\Desktop\VultrDriveDesktop
python app.py
```

**Desde el portable:**
- Doble clic en `VultrDriveDesktop.exe`

### Crear Acceso Directo de Backup en el Escritorio

```powershell
python create_shortcut.py
```

Esto creará un acceso directo llamado "Vultr Backup Now" en tu escritorio.

## 📖 Guía de Uso

### 1. Configurar un Perfil

1. Abre la aplicación
2. Haz clic en "⚙️ Gestionar Perfiles"
3. Completa el formulario:
   - **Nombre del Perfil**: Nombre descriptivo (ej: "Producción")
   - **Access Key**: Tu Access Key de Vultr
   - **Secret Key**: Tu Secret Key de Vultr
   - **Hostname**: El hostname de tu región (ej: `lax1.vultrobjects.com`)
4. Haz clic en "Guardar Perfil"

### 2. Subir Archivos

1. Selecciona tu perfil en la pestaña "Principal"
2. Elige el bucket de destino
3. Haz clic en "📁 Subir Archivo"
4. Selecciona el archivo
5. Espera a que se complete la subida

### 3. Hacer Backup de una Carpeta

1. Selecciona tu perfil y bucket
2. Haz clic en "💾 Backup de Carpeta"
3. Selecciona la carpeta que deseas respaldar
4. La barra de progreso mostrará el avance
5. Recibirás una confirmación al finalizar

### 4. Montar como Disco

1. Ve a la pestaña "Montar Disco"
2. Selecciona la letra de unidad (V, W, X, Y, Z)
3. Asegúrate de tener un perfil y bucket seleccionados
4. Haz clic en "🔗 Montar Unidad"
5. ¡Accede desde "Este equipo"!

**Características del montaje:**
- ✅ Cache VFS para mejor rendimiento
- ✅ Auto-desmontaje al cerrar
- ✅ Soporte multi-máquina (sin conflictos de timestamps)
- ✅ Sincronización cada 15 segundos

**Para desmontar:**
- Haz clic en "🔌 Desmontar Unidad"
- O cierra la aplicación (se desmonta automáticamente)

### 5. Cambiar Idioma

1. Haz clic en el selector de idioma en la esquina superior derecha
2. Elige tu idioma preferido
3. La interfaz cambia instantáneamente
4. El idioma se guarda automáticamente

## 🏗️ Estructura del Proyecto

```
VultrDriveDesktop/
├── app.py                          # Aplicación principal con startup optimizado
├── splash_screen.py                # Splash screen rediseñado
├── translations.py                 # Sistema multiidioma (5 idiomas)
├── s3_handler.py                   # Gestión de operaciones S3/Vultr
├── config_manager.py               # Gestión de perfiles y configuración
├── rclone_manager.py               # Montaje de disco + auto-detección
├── file_watcher.py                 # Monitoreo de archivos (tiempo real)
├── backup_now.py                   # Script de backup rápido
├── create_shortcut.py              # Creador de acceso directo
├── config.json                     # Almacenamiento de perfiles
├── config.example.json             # Ejemplo de configuración
├── user_preferences.json           # Preferencias del usuario (idioma, tema)
├── requirements.txt                # Dependencias Python
├── setup.py                        # Script de instalación
├── EMPAQUETAR.bat                  # Script de compilación
├── compilar_y_empaquetar.ps1       # Automatización PowerShell
├── ui/
│   ├── main_window.py              # Interfaz principal (100% traducida)
│   ├── settings_window.py          # Ventana de configuración
│   └── style.qss                   # Hoja de estilos Qt
├── rclone-v1.71.2-windows-amd64/   # Rclone incluido
│   └── rclone.exe
└── docs/
    ├── QUICK_START.md              # Inicio rápido
    ├── TRADUCCIONES_COMPLETAS.md   # Documentación de traducciones
    ├── COMO_COMPILAR_Y_EMPAQUETAR.md
    └── INDICE_DOCUMENTACION.md
```

## 🔧 Compilar Version Portable

Si deseas compilar tu propia versión portable:

```powershell
# Método 1: Script automatizado (Recomendado)
.\compilar_y_empaquetar.ps1

# Método 2: Script batch
.\EMPAQUETAR.bat

# Método 3: Manual
pyinstaller --onefile --windowed --icon=icon.ico app.py
```

Consulta `COMO_COMPILAR_Y_EMPAQUETAR.md` para instrucciones detalladas.

## ⚡ Rendimiento

### Benchmarks v2.0

- **Import translations.py**: 24.45ms
- **Lazy loading (first)**: 0.07ms  
- **Cached access**: 0.0019ms
- **Startup completo**: ~500ms
- **Cambio de idioma**: <5ms
- **Portable size**: 170MB (125MB ZIP)

### Optimizaciones Implementadas

1. **Lazy Loading**: Las traducciones se cargan solo cuando se necesitan
2. **Cache Inteligente**: Traducciones se cachean en memoria
3. **Post-Window Init**: Funciones pesadas se ejecutan después del show()
4. **VFS Cache**: Rclone usa cache para mejor performance
5. **Startup Asíncrono**: QTimer.singleShot para operaciones no bloqueantes

## 🐛 Solución de Problemas

### La unidad no se monta

**Posibles causas:**
1. WinFsp no instalado
2. Letra de unidad en uso
3. Credenciales incorrectas
4. Bucket no existe

**Solución:**
```powershell
# Verificar WinFsp
.\verificar_winfsp.ps1

# Si no está instalado
.\VultrDriveDesktop-Portable\INSTALAR_WINFSP.bat
```

### Error al subir archivos

- ✅ Verifica tu conexión a internet
- ✅ Confirma que las credenciales sean válidas
- ✅ Asegúrate de que el bucket exista y tengas permisos
- ✅ Revisa que el archivo no esté en uso

### La aplicación no inicia

```powershell
# Reinstalar dependencias
pip install --upgrade -r requirements.txt

# Verificar Python
python --version  # Debe ser 3.9+

# Modo verbose para ver errores
python app.py --verbose
```

### WinFsp se reinstala cada vez

**Esto ya está solucionado en v2.0**, pero si persiste:
1. Verifica que WinFsp esté instalado en `C:\Program Files (x86)\WinFsp`
2. Ejecuta `.\verificar_winfsp.ps1` para confirmar
3. Si aparece "WinFsp NO encontrado" pero está instalado, reporta el bug

### Montaje falla en múltiples máquinas

**v2.0 incluye soporte multi-máquina**, pero considera:
- Evita modificar el mismo archivo simultáneamente en múltiples máquinas
- El cache VFS se sincroniza cada 15 segundos
- Flags usados: `--no-modtime`, `--no-checksum` para evitar conflictos

## 🤝 Contribuir

¡Las contribuciones son bienvenidas!

1. Fork el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

### Agregar un nuevo idioma

Para agregar soporte para un nuevo idioma:

1. Edita `translations.py`
2. Agrega un nuevo método `_tu_idioma()`
3. Traduce todas las 60+ claves
4. Agrega el idioma al método `get_supported_languages()`
5. Incluye la bandera emoji correspondiente

Ver `TRADUCCIONES_COMPLETAS.md` para detalles.

## 📋 Roadmap

### v2.1 (En desarrollo)
- [ ] Sincronización bidireccional en tiempo real
- [ ] Bandeja del sistema (system tray)
- [ ] Notificaciones push para operaciones largas
- [ ] Modo oscuro mejorado

### v3.0 (Futuro)
- [ ] Cifrado end-to-end
- [ ] Versionado de archivos (historial)
- [ ] Backups programados (scheduler)
- [ ] Interfaz web (opcional)
- [ ] Soporte para Linux y macOS
- [ ] API REST para integración

## 📝 Changelog

### v2.0 (Noviembre 2025)
- ✨ 5 idiomas completos con lazy loading
- ✨ Instalación inteligente de WinFsp (condicional)
- ✨ Limpieza automática de unidades al iniciar
- ✨ Splash screen rediseñado
- ✨ Soporte multi-máquina sin conflictos
- ✨ Mensajes de error detallados en español
- ⚡ Optimización de startup (500ms)
- 🐛 100+ bugfixes y mejoras de estabilidad

### v1.0 (Octubre 2025)
- 🎉 Lanzamiento inicial
- Gestión de perfiles
- Montaje de disco básico
- Upload/backup de archivos
- Soporte ES/EN

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para más detalles.

## 🙏 Créditos

Desarrollado con:
- **PyQt6** - Interfaz de usuario moderna y responsive
- **boto3** - SDK de AWS S3 (compatible con Vultr Object Storage)
- **rclone** - Montaje de almacenamiento en la nube
- **watchdog** - Monitoreo de sistema de archivos
- **pywin32** - Integración con Windows

### Recursos Utilizados
- Iconos: [Font Awesome](https://fontawesome.com/)
- Banderas emoji: Unicode Consortium
- Inspiración UI: Material Design

## 📞 Soporte

- 📧 Email: soporte@example.com
- 🐛 Issues: [GitHub Issues](https://github.com/aprendeineamx-max/VultrDriveDesktop/issues)
- 📖 Docs: [Wiki](https://github.com/aprendeineamx-max/VultrDriveDesktop/wiki)
- 💬 Discussions: [GitHub Discussions](https://github.com/aprendeineamx-max/VultrDriveDesktop/discussions)

## 🔗 Enlaces Útiles

- [Vultr Object Storage Docs](https://www.vultr.com/docs/vultr-object-storage/)
- [Rclone Documentation](https://rclone.org/docs/)
- [WinFsp Download](https://winfsp.dev/rel/)
- [PyQt6 Documentation](https://www.riverbankcomputing.com/static/Docs/PyQt6/)

---

**⭐ Si este proyecto te es útil, considera darle una estrella en GitHub!**

Made with ❤️ by [aprendeineamx-max](https://github.com/aprendeineamx-max)
