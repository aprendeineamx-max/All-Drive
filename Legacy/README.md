# VultrDrive Desktop 🚀

**Sistema de montaje y sincronización de almacenamiento Vultr S3 como unidad local en Windows**

[![Portable](https://img.shields.io/badge/Portable-100%25-brightgreen)](docs/SISTEMA_PORTABLE_COMPLETO.md)
[![WinFsp](https://img.shields.io/badge/WinFsp-Auto--Install-blue)](docs/INSTALACION_AUTOMATICA_WINFSP.md)
[![Windows](https://img.shields.io/badge/Windows-10%2F11-0078D6)](https://www.microsoft.com/windows)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB)](https://www.python.org/)

---

## ✨ Características Principales

- 🔌 **Montaje de unidades** - Monta tu almacenamiento Vultr S3 como disco local (V:, W:, X:, etc.)
- 🔄 **Sincronización bidireccional** - Sincroniza archivos entre local y nube
- 📦 **100% Portable** - Funciona en cualquier PC Windows sin instalación
- 🤖 **Instalación automática** - WinFsp se instala automáticamente al primer uso
- 🌐 **Multi-idioma** - Español e Inglés
- 🎨 **Temas** - Dark y Light theme
- ⚡ **Rápido y ligero** - Inicio en menos de 3 segundos

---

## 🚀 Inicio Rápido

### 1️⃣ Ejecutar el Programa

```batch
ejecutar_app.bat
```

### 2️⃣ Primera Vez (instalación automática de WinFsp)

1. Se detecta que WinFsp no está instalado
2. Aparece ventana UAC pidiendo permisos
3. Haz clic en **"Sí"**
4. WinFsp se instala automáticamente (~10 seg)
5. ¡El programa inicia!

### 3️⃣ Configurar Credenciales

1. Ve a la pestaña **"Avanzado"**
2. Ingresa tus credenciales de Vultr S3:
   - Access Key ID
   - Secret Access Key
   - Endpoint URL
   - Bucket Name
3. Guarda la configuración

### 4️⃣ Montar Unidad

1. Ve a la pestaña **"Montar Disco"**
2. Selecciona letra de unidad (V:, W:, etc.)
3. Haz clic en **"Montar como Unidad"**
4. ¡Tu disco aparece en el Explorador de Windows!

---

## 📂 Estructura del Proyecto

```
VultrDriveDesktop/
│
├── 📄 ejecutar_app.bat          ← EJECUTA ESTO para iniciar
├── 📄 app.py                    ← Código principal
├── 📄 config.json               ← Configuración
├── 📄 requirements.txt          ← Dependencias Python
├── 📄 LICENSE                   ← Licencia MIT
├── 📄 LEEME_PRIMERO.txt         ← Guía de inicio rápido
│
├── 📁 ui/                       ← Interfaz gráfica (PyQt6)
│   ├── main_window.py
│   ├── settings_window.py
│   └── style.qss
│
├── 📁 dependencies/             ← Componentes necesarios
│   └── winfsp-2.0.23075.msi    ← Instalador WinFsp (2.1 MB)
│
├── 📁 rclone-v1.71.2-windows-amd64/  ← Rclone portable
│   └── rclone.exe
│
├── 📁 docs/                     ← 📚 DOCUMENTACIÓN
│   ├── README.md                     → Índice de docs
│   ├── SISTEMA_PORTABLE_COMPLETO.md  → Guía completa
│   ├── INSTALACION_AUTOMATICA_WINFSP.md
│   ├── QUICK_START.md
│   ├── SECURITY.md
│   └── ... más guías
│
├── 📁 scripts/                  ← 🔧 SCRIPTS DE UTILIDAD
│   ├── README.md                     → Índice de scripts
│   ├── check_portable.ps1            → Verificar componentes
│   ├── crear_distribucion_portable.ps1
│   └── ... más scripts
│
├── 📁 tests/                    ← 🧪 TESTS Y PRUEBAS
│   ├── README.md
│   ├── test_performance.py
│   └── ... más tests
│
└── 📁 archive/                  ← 📦 ARCHIVO HISTÓRICO
    └── ... documentos antiguos
```

---

## 📚 Documentación

| Documento | Descripción |
|-----------|-------------|
| **[LEEME_PRIMERO.txt](LEEME_PRIMERO.txt)** | 🚀 **EMPIEZA AQUÍ** - Guía rápida |
| [docs/SISTEMA_PORTABLE_COMPLETO.md](docs/SISTEMA_PORTABLE_COMPLETO.md) | Sistema portable completo |
| [docs/INSTALACION_AUTOMATICA_WINFSP.md](docs/INSTALACION_AUTOMATICA_WINFSP.md) | Instalación automática WinFsp |
| [docs/QUICK_START.md](docs/QUICK_START.md) | Inicio rápido |
| [docs/SECURITY.md](docs/SECURITY.md) | Seguridad y privacidad |
| [docs/README.md](docs/README.md) | Índice completo de documentación |

---

## 🛠️ Requisitos

### Sistema Operativo
- **Windows 10/11** (64-bit)
- Permisos de administrador (solo para instalar WinFsp)

### Automáticamente Incluido
- ✅ **Rclone** (portable, incluido)
- ✅ **WinFsp** (se instala automáticamente)
- ✅ **Python** (si usas el ejecutable empaquetado)

### Si ejecutas desde Python
```bash
pip install -r requirements.txt
```

Dependencias:
- PyQt6 >= 6.6.0
- boto3 >= 1.34.0
- watchdog >= 4.0.0
- pywin32 >= 306

---

## 🎯 Características Avanzadas

### Montaje de Unidades
- Monta buckets S3 como discos locales (V:, W:, X:, Y:, Z:)
- Acceso en tiempo real vía Explorador de Windows
- Detección automática de unidades montadas
- Desmontaje limpio y seguro

### Sincronización
- Sincronización bidireccional automática
- Detección de cambios en tiempo real
- Sincronización manual bajo demanda
- Logs detallados de operaciones

### Configuración
- Multi-cuenta (múltiples credenciales S3)
- Configuración persistente
- Importar/Exportar configuración
- Tema personalizable (Dark/Light)

---

## 🔧 Scripts de Utilidad

Ver carpeta: [`scripts/`](scripts/)

### Empaquetado y Distribución
```powershell
.\scripts\crear_distribucion_portable.ps1    # Crear versión portable
.\scripts\compilar_y_empaquetar.ps1          # Compilar a .exe
```

### Verificación
```powershell
.\scripts\check_portable.ps1                 # Verificar componentes
.\scripts\verificar_winfsp.ps1               # Verificar WinFsp
```

### Instalación
```powershell
.\scripts\instalar_winfsp.ps1                # Instalar WinFsp manualmente
```

---

## 🧪 Tests

Ver carpeta: [`tests/`](tests/)

```bash
# Test de rendimiento
python tests\test_performance.py

# Test de traducciones
python tests\test_translations.py

# Benchmark de inicio
python tests\benchmark_startup.py
```

---

## 📦 Distribución Portable

### Crear Versión para Distribuir

```powershell
cd scripts
.\crear_distribucion_portable.ps1
```

Esto crea una carpeta `VultrDrive_Portable_YYYYMMDD_HHMMSS/` lista para:
- Copiar a otro PC
- Compartir con usuarios
- Subir a servidor
- Guardar en USB

### Características Portables

✅ **No requiere instalación** - Solo copiar y ejecutar  
✅ **Incluye todo lo necesario** - WinFsp, Rclone, etc.  
✅ **Funciona offline** - Sin necesidad de internet para instalar  
✅ **Cualquier ubicación** - Escritorio, USB, Documentos, etc.  
✅ **Auto-instala WinFsp** - Primera vez pide permisos UAC  

---

## 🔐 Seguridad

- Credenciales encriptadas localmente
- Comunicación HTTPS con Vultr S3
- WinFsp: Software de código abierto y auditado
- Sin telemetría ni tracking
- Datos almacenados localmente

Ver: [docs/SECURITY.md](docs/SECURITY.md)

---

## 🐛 Solución de Problemas

### ❌ "No se pudo instalar WinFsp"
**Solución**: Ejecuta como administrador
```batch
Clic derecho en ejecutar_app.bat → "Ejecutar como administrador"
```

### ❌ "No se encontró el instalador MSI"
**Solución**: Verifica que existe `dependencies\winfsp-2.0.23075.msi`

### ❌ No se puede montar la unidad
**Solución**:
1. Verifica que WinFsp está instalado: `scripts\verificar_winfsp.ps1`
2. Verifica credenciales en configuración
3. Revisa logs en la pestaña de sincronización

### 🔍 Más ayuda
Ver: [docs/INSTALACION_AUTOMATICA_WINFSP.md](docs/INSTALACION_AUTOMATICA_WINFSP.md)

---

## 🤝 Contribuir

Las contribuciones son bienvenidas. Por favor:

1. Fork el repositorio
2. Crea una rama para tu feature: `git checkout -b feature/nueva-caracteristica`
3. Commit tus cambios: `git commit -am 'Añade nueva característica'`
4. Push a la rama: `git push origin feature/nueva-caracteristica`
5. Abre un Pull Request

---

## 📄 Licencia

Este proyecto está bajo la licencia MIT. Ver [LICENSE](LICENSE) para más detalles.

---

## 🔗 Enlaces Útiles

- **Vultr**: https://vultr.com
- **WinFsp**: https://winfsp.dev
- **Rclone**: https://rclone.org
- **PyQt6**: https://www.riverbankcomputing.com/software/pyqt/

---

## 📞 Soporte

¿Necesitas ayuda?

1. Lee la documentación en [`docs/`](docs/)
2. Revisa [LEEME_PRIMERO.txt](LEEME_PRIMERO.txt)
3. Ejecuta `scripts\check_portable.ps1` para diagnosticar
4. Abre un issue en GitHub

---

## 📝 Changelog

### Versión Actual (Noviembre 2025)
- ✅ Sistema portable 100% funcional
- ✅ Instalación automática de WinFsp
- ✅ Instalador incluido (dependencies/)
- ✅ Documentación completa
- ✅ Estructura organizada
- ✅ Scripts de utilidad
- ✅ Tests incluidos

---

## 🎉 Créditos

Desarrollado con ❤️ para usuarios de Vultr

**Tecnologías utilizadas**:
- Python 3.11+
- PyQt6
- Rclone
- WinFsp
- Boto3 (AWS SDK para S3)

---

**¡Gracias por usar VultrDrive Desktop!** 🚀

Si te gusta el proyecto, ¡dale una ⭐ en GitHub!
