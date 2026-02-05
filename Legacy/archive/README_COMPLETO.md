# 🚀 VultrDriveDesktop v2.0

<div align="center">

![Version](https://img.shields.io/badge/version-2.0-blue)
![Platform](https://img.shields.io/badge/platform-Windows-blue)
![Python](https://img.shields.io/badge/python-3.14-green)
![License](https://img.shields.io/badge/license-MIT-green)

**Cliente de escritorio profesional para Vultr Object Storage**

[Características](#-características) • [Instalación](#-instalación-rápida) • [Uso](#-uso) • [Requisitos](#-requisitos) • [Soporte](#-soporte)

</div>

---

## ✨ Características

### 🌍 **Multiidioma**
- 🇪🇸 Español
- 🇺🇸 English  
- 🇫🇷 Français
- Cambio instantáneo desde la interfaz

### 🎨 **Temas Personalizables**
- 🌙 **Tema Oscuro** - Para trabajo nocturno
- ☀️ **Tema Claro** - Para máxima legibilidad
- Conmutación con un solo clic

### 📦 **Gestión de Almacenamiento**
- ✅ Crear, listar y eliminar buckets
- ✅ Subir archivos individuales o carpetas completas
- ✅ Descargar archivos y carpetas
- ✅ Eliminar objetos
- ✅ Vista en árbol navegable

### 💾 **Montar como Disco**
- ✅ Accede a tu Vultr Storage como una unidad local (W:, X:, Y:, Z:)
- ✅ Arrastra y suelta archivos directamente
- ✅ Compatible con todos los programas de Windows
- ✅ Caché inteligente para mejor rendimiento

### ⚡ **Sincronización en Tiempo Real**
- ✅ Monitoreo automático de carpetas locales
- ✅ Subida instantánea de cambios
- ✅ Detección de archivos nuevos, modificados y eliminados
- ✅ Estado en tiempo real

### 🔐 **Gestión de Perfiles**
- ✅ Múltiples cuentas de Vultr
- ✅ Cambio rápido entre perfiles
- ✅ Configuración segura almacenada localmente

### 💾 **Backup Completo**
- ✅ Respaldo de carpetas enteras
- ✅ Preservación de estructura de directorios
- ✅ Barra de progreso en tiempo real

---

## 🔧 Requisitos

### Software Necesario

| Software | Versión | Propósito | Estado |
|----------|---------|-----------|--------|
| **Python** | 3.8+ | Runtime de la aplicación | ✅ Requerido |
| **PyQt6** | 6.x | Framework de interfaz gráfica | ✅ Requerido |
| **boto3** | Latest | Cliente AWS S3 (compatible Vultr) | ✅ Requerido |
| **watchdog** | Latest | Monitoreo de archivos | ✅ Requerido |
| **Rclone** | 1.71.2+ | Montaje de unidades | ✅ Incluido |
| **WinFsp** | 2.0+ | Sistema de archivos virtual | ⚠️ Requerido para montar |

### Credenciales de Vultr

Para usar la aplicación necesitas:
1. Una cuenta en [Vultr.com](https://vultr.com)
2. Object Storage configurado
3. Credenciales de acceso:
   - **Access Key** (ID de clave de acceso)
   - **Secret Key** (Clave secreta)
   - **Host Base** (URL del endpoint, ej: `ewr1.vultrobjects.com`)

---

## 🚀 Instalación Rápida

### Opción 1: Instalación Automática (Recomendada)

```powershell
# 1. Clonar o descargar el proyecto
cd C:\Users\TuUsuario\Desktop\VultrDriveDesktop

# 2. Ejecutar instalador automático
.\setup.ps1
```

El instalador automático:
- ✅ Verifica Python
- ✅ Instala dependencias (PyQt6, boto3, watchdog)
- ✅ Descarga Rclone
- ✅ Crea acceso directo en el escritorio

### Opción 2: Instalación Manual

```powershell
# 1. Instalar dependencias Python
pip install -r requirements.txt

# 2. Descargar Rclone (ya incluido en el proyecto)
# Alternativamente: https://rclone.org/downloads/

# 3. Instalar WinFsp (para montar unidades)
.\instalar_winfsp.ps1
# O descarga manual: https://winfsp.dev/rel/
```

---

## 🎮 Uso

### Iniciar la Aplicación

**Método 1**: Acceso directo del escritorio
- Doble clic en **VultrDriveDesktop** 🖱️

**Método 2**: Línea de comandos
```powershell
# Opción A - Script batch
.\start.bat

# Opción B - Script PowerShell
.\start.ps1

# Opción C - Python directo
py app.py
```

### Configuración Inicial

#### 1️⃣ **Crear un Perfil**
```
Configuración → Agregar Perfil
- Nombre del perfil: Mi-Cuenta-Vultr
- Access Key: (tu clave de acceso)
- Secret Key: (tu clave secreta)
- Host Base: ewr1.vultrobjects.com
- Región: ewr1
→ Guardar
```

#### 2️⃣ **Cambiar Idioma** (Opcional)
```
Botón 🌍 (arriba izquierda) → Seleccionar idioma
```

#### 3️⃣ **Cambiar Tema** (Opcional)
```
Botón 🌙/☀️ (arriba derecha) → Alternar tema
```

### Operaciones Principales

#### 📦 **Gestionar Buckets**
```
Tab "Principal"
→ Crear Bucket: Introduce nombre y haz clic en "Crear Bucket"
→ Ver contenido: Selecciona bucket en el dropdown
→ Subir archivo: Clic en "📤 Subir Archivo"
→ Subir carpeta: Clic en "📁 Subir Carpeta"
```

#### 💾 **Montar como Disco**
```
Tab "Montar Disco"
→ Seleccionar letra de unidad (W:, X:, Y:, Z:)
→ Seleccionar bucket a montar
→ Clic en "🔗 Montar Unidad"
→ Acceder desde "Este Equipo" en Windows Explorer
```

⚠️ **Importante**: WinFsp debe estar instalado para usar esta función.

#### ⚡ **Sincronización Automática**
```
Tab "Sincronización en Tiempo Real"
→ Clic en "📁 Seleccionar Carpeta"
→ Elegir carpeta a sincronizar
→ Clic en "▶️ Iniciar Sincronización"
→ Los cambios se subirán automáticamente
```

#### 💾 **Backup Completo**
```
Tab "Avanzado"
→ Clic en "📁 Seleccionar Carpeta"
→ Elegir carpeta a respaldar
→ Clic en "💾 Hacer Backup Completo"
→ Esperar a que termine (ver barra de progreso)
```

---

## 🔧 Solución de Problemas

### ❌ Error: "WinFsp no está instalado"

**Síntoma**: Al intentar montar una unidad aparece error sobre WinFsp.

**Solución**:
```powershell
# Opción 1: Automática
.\instalar_winfsp.ps1

# Opción 2: Manual
# 1. Visita: https://winfsp.dev/rel/
# 2. Descarga: winfsp-2.0.23075.msi
# 3. Instala el archivo MSI
# 4. Reinicia VultrDriveDesktop
```

**Verificar instalación**:
```powershell
.\verificar_winfsp.ps1
```

### ❌ Error: "Python no encontrado"

**Solución**:
```powershell
# Descarga Python desde: https://python.org
# Durante instalación marca: "Add Python to PATH"
```

### ❌ Error: "Módulo PyQt6 no encontrado"

**Solución**:
```powershell
py -m pip install PyQt6 boto3 watchdog
```

### ❌ Error al conectar con Vultr

**Verificar**:
- ✅ Access Key y Secret Key correctas
- ✅ Host Base correcto (ejemplo: `ewr1.vultrobjects.com`)
- ✅ Object Storage habilitado en tu cuenta Vultr
- ✅ Conexión a internet activa

---

## 📁 Estructura del Proyecto

```
VultrDriveDesktop/
├── app.py                      # Punto de entrada de la aplicación
├── config_manager.py           # Gestión de perfiles y configuración
├── s3_handler.py              # Operaciones S3/Vultr Storage
├── rclone_manager.py          # Montaje de unidades con Rclone
├── file_watcher.py            # Sincronización en tiempo real
├── translations.py            # Sistema de traducción (ES/EN/FR)
├── theme_manager.py           # Gestión de temas (Dark/Light)
├── ui/
│   ├── main_window.py         # Ventana principal de la aplicación
│   ├── settings_window.py     # Ventana de configuración
│   └── style.qss              # Estilos CSS de la interfaz
├── rclone-v1.71.2-windows-amd64/
│   └── rclone.exe             # Ejecutable de Rclone
├── start.bat                  # Iniciador Windows (batch)
├── start.ps1                  # Iniciador Windows (PowerShell)
├── setup.ps1                  # Instalador automático
├── instalar_winfsp.ps1        # Instalador de WinFsp
├── verificar_winfsp.ps1       # Verificador de WinFsp
├── verificar.ps1              # Diagnóstico del sistema
├── requirements.txt           # Dependencias Python
├── config.json                # Configuración de perfiles (creado al uso)
└── user_preferences.json      # Preferencias del usuario (idioma/tema)
```

---

## 📚 Scripts Útiles

| Script | Descripción |
|--------|-------------|
| `start.bat` | Inicia la aplicación (Windows Batch) |
| `start.ps1` | Inicia la aplicación (PowerShell) |
| `setup.ps1` | Instalador completo automático |
| `instalar_winfsp.ps1` | Instala WinFsp para montar unidades |
| `verificar_winfsp.ps1` | Verifica instalación de WinFsp |
| `verificar.ps1` | Diagnóstico completo del sistema |

---

## 🔐 Seguridad

- ✅ Las credenciales se almacenan localmente en `config.json`
- ✅ No se envían datos a terceros (excepto Vultr)
- ✅ Conexiones HTTPS encriptadas
- ⚠️ **Recomendación**: No compartas tu archivo `config.json`
- ⚠️ **Recomendación**: Usa contraseñas seguras en Vultr

---

## 📝 Documentación Adicional

- [QUICK_START.md](QUICK_START.md) - Guía de inicio rápido
- [IMPLEMENTACION_COMPLETA.md](IMPLEMENTACION_COMPLETA.md) - Detalles técnicos
- [MEJORAS_IMPLEMENTADAS.md](MEJORAS_IMPLEMENTADAS.md) - Changelog v2.0
- [SOLUCION_MONTAJE.md](SOLUCION_MONTAJE.md) - Guía de solución de problemas de montaje
- [CORRECCIONES_APLICADAS.md](CORRECCIONES_APLICADAS.md) - Correcciones y fixes

---

## 🤝 Contribuir

Las contribuciones son bienvenidas! Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

---

## 📞 Soporte

¿Necesitas ayuda? 

1. **Documentación**: Revisa los archivos `.md` en el proyecto
2. **Diagnóstico**: Ejecuta `.\verificar.ps1` para diagnóstico automático
3. **Issues**: Reporta problemas en GitHub Issues
4. **Vultr Support**: Para problemas de cuenta: https://my.vultr.com/support/

---

## 📜 Licencia

Este proyecto está bajo la Licencia MIT. Ver archivo `LICENSE` para más detalles.

---

## 🌟 Agradecimientos

- **Vultr** - Por proporcionar Object Storage S3-compatible
- **Rclone** - Por la excelente herramienta de sincronización en la nube
- **WinFsp** - Por hacer posible los sistemas de archivos virtuales en Windows
- **PyQt6** - Por el framework de interfaz gráfica

---

## 📊 Changelog

### v2.0 (Noviembre 2025)
- ✅ Sistema multiidioma (ES/EN/FR)
- ✅ Temas Dark/Light conmutables
- ✅ Mejoras en montaje de unidades
- ✅ Corrección de errores de daemon mode
- ✅ Mensajes de error mejorados
- ✅ Scripts de instalación automática
- ✅ Documentación completa

### v1.0 (Octubre 2025)
- ✅ Versión inicial
- ✅ Gestión básica de buckets
- ✅ Subida/descarga de archivos
- ✅ Sincronización en tiempo real
- ✅ Backup completo

---

<div align="center">

**Hecho con ❤️ para la comunidad**

[⬆ Volver arriba](#-vultrdrivedeskto-v20)

</div>
