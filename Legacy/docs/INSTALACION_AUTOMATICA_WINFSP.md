# 🚀 Instalación Automática de WinFsp - Sistema Portable

## ✨ ¿Qué es esto?

**VultrDrive Desktop** ahora incluye un sistema de instalación automática de WinFsp que hace que el programa sea **completamente portable** y fácil de usar en cualquier PC con Windows.

## 🎯 ¿Cómo funciona?

### 1. **Primera Ejecución**
Cuando ejecutas `VultrDrive Desktop` en una PC donde **nunca se ha instalado WinFsp**:

1. El programa detecta automáticamente que WinFsp no está instalado
2. Muestra un mensaje en la pantalla de inicio: "Instalando componentes requeridos (WinFsp)..."
3. **Instala WinFsp automáticamente** usando el instalador incluido en la carpeta `dependencies/`
4. Aparecerá una ventana de UAC (Control de Cuentas de Usuario) pidiendo permisos de administrador
5. Haz clic en **"Sí"** para permitir la instalación
6. El programa continúa iniciándose normalmente

### 2. **Ejecuciones Posteriores**
Una vez WinFsp está instalado:
- El programa detecta que ya está instalado
- **NO vuelve a instalar** WinFsp
- Inicia directamente sin demoras

## 📦 Estructura Portable

```
VultrDriveDesktop/
├── app.py                          # Programa principal
├── dependencies/                    # ⭐ Carpeta con instaladores
│   └── winfsp-2.0.23075.msi        # Instalador de WinFsp (2.1 MB)
├── rclone-v1.71.2-windows-amd64/   # Rclone portable
│   └── rclone.exe
├── ui/                              # Interfaz gráfica
├── config.json                      # Configuración
└── ... otros archivos del programa
```

## 🎁 Ventajas del Sistema Portable

✅ **Sin instalación manual**: WinFsp se instala automáticamente la primera vez
✅ **Totalmente portable**: Copia la carpeta a cualquier PC y funciona
✅ **Sin conexión a internet**: El instalador de WinFsp está incluido
✅ **Funciona en cualquier ubicación**: Escritorio, Documentos, USB, etc.
✅ **Detección inteligente**: No reinstala si ya está presente
✅ **Instalación silenciosa**: Sin ventanas molestas (solo UAC)

## 🔧 ¿Qué hace el instalador automático?

1. **Busca el instalador**: Revisa en `dependencies/`, `winfsp/` y la carpeta raíz
2. **Ejecuta la instalación**: Usa PowerShell con privilegios elevados
3. **Instala silenciosamente**: Parámetros `/quiet /norestart`
4. **Verifica la instalación**: Confirma que WinFsp se instaló correctamente
5. **Registra todo**: Mensajes de depuración en la consola

## 🚨 Solución de Problemas

### ❌ "No se pudo instalar WinFsp automáticamente"

**Causa**: El usuario canceló la ventana UAC o no tiene permisos de administrador

**Solución**:
1. Cierra el programa
2. Haz clic derecho en `ejecutar_app.bat`
3. Selecciona **"Ejecutar como administrador"**
4. Cuando aparezca UAC, haz clic en **"Sí"**

### ❌ "No se encontró el instalador MSI"

**Causa**: Falta el archivo `winfsp-2.0.23075.msi` en la carpeta `dependencies/`

**Solución**:
1. Descarga WinFsp desde: https://github.com/winfsp/winfsp/releases/download/v2.0/winfsp-2.0.23075.msi
2. Guarda el archivo en: `VultrDriveDesktop/dependencies/winfsp-2.0.23075.msi`
3. Ejecuta el programa nuevamente

### ❌ "WinFsp no se detectó después de la instalación"

**Causa**: La instalación se completó pero necesita reiniciar el programa

**Solución**:
1. Cierra completamente el programa
2. Abre el programa nuevamente
3. WinFsp ya debería estar disponible

## 📱 Instalación Manual (Si falla la automática)

Si por alguna razón la instalación automática no funciona:

**Opción 1**: Usa el script incluido
```batch
INSTALAR_WINFSP.bat
```

**Opción 2**: Instala manualmente
1. Abre la carpeta `dependencies/`
2. Haz doble clic en `winfsp-2.0.23075.msi`
3. Sigue el asistente de instalación
4. Reinicia `VultrDrive Desktop`

## 🎯 Creación de Versión Portable

Para crear una versión portable completa:

```powershell
# Asegúrate de que está el instalador de WinFsp
.\crear_portable.ps1
```

Esto creará una carpeta `VultrDrive_Portable/` lista para copiar a cualquier PC.

## 📋 Requisitos del Sistema

- **Sistema Operativo**: Windows 10/11 (64-bit)
- **Permisos**: Administrador (solo para instalar WinFsp)
- **Espacio**: ~50 MB (incluye WinFsp + Rclone)
- **Python**: No requerido (si usas el ejecutable empaquetado)

## 🔐 Seguridad

- **WinFsp es seguro**: Software de código abierto y gratuito
- **Verificación oficial**: Instalador descargado desde GitHub oficial
- **Sin malware**: MD5 del archivo verificado
- **UAC requerido**: Windows solicita permisos explícitos

## 💡 Notas Técnicas

### ¿Por qué necesita permisos de administrador?

WinFsp instala un **driver del sistema** (controlador de kernel) que permite montar unidades virtuales en Windows. Los drivers solo pueden instalarse con permisos de administrador por seguridad.

### ¿WinFsp se queda instalado en el sistema?

**Sí**, WinFsp se instala en:
```
C:\Program Files (x86)\WinFsp\
```

Esto es **normal y necesario**. Es un componente del sistema que permite montar unidades, similar a cómo funciona el soporte de red de Windows.

### ¿Se puede desinstalar WinFsp?

**Sí**, puedes desinstalarlo desde:
- Panel de Control → Programas y características → WinFsp
- O ejecutando el MSI nuevamente

**⚠️ IMPORTANTE**: Si desinstalas WinFsp, `VultrDrive Desktop` **no podrá montar unidades**. Solo podrás usar las funciones de sincronización.

## 📚 Más Información

- **WinFsp**: https://winfsp.dev/
- **Código fuente**: https://github.com/winfsp/winfsp
- **Documentación**: https://winfsp.dev/doc/

---

**¿Dudas?** Revisa el archivo `README.md` principal o contacta al desarrollador.

