# 🎯 Guía Rápida - VultrDriveDesktop v2.0

## ⚡ Inicio Rápido (3 pasos)

### 1️⃣ Iniciar la Aplicación
```
🖱️ Doble clic en: VultrDriveDesktop (acceso directo del escritorio)
```

### 2️⃣ Configurar Perfil
```
Configuración → ➕ Agregar Perfil
├─ Nombre: Mi-Cuenta-Vultr
├─ Access Key: [tu clave]
├─ Secret Key: [tu clave secreta]
├─ Host Base: ewr1.vultrobjects.com
└─ Región: ewr1
→ 💾 Guardar
```

### 3️⃣ ¡Listo para usar!
```
✅ Subir archivos
✅ Crear buckets
✅ Montar como disco
✅ Sincronizar carpetas
```

---

## 🌍 NUEVO: Cambiar Idioma

```
┌─────────────────────────────────┐
│  🌍 Idioma    [v] 🌙 Dark Theme │  ← Controles superiores
├─────────────────────────────────┤
│                                 │
│  ┌─ Clic aquí ─┐                │
│  │ 🌍 Idioma   │                │
│  └──────────────┘                │
│        │                         │
│        ├─ 🇪🇸 ES Español         │
│        ├─ 🇺🇸 EN English         │
│        └─ 🇫🇷 FR Français        │
│                                 │
└─────────────────────────────────┘
```

**Efecto**: La interfaz completa cambia al idioma seleccionado instantáneamente.

---

## 🎨 NUEVO: Cambiar Tema

```
┌─────────────────────────────────┐
│  🌍 Idioma  [🌙 Dark Theme] ←── Clic aquí │
├─────────────────────────────────┤
│                                 │
│  🌙 Dark Theme  ──→  ☀️ Light Theme │
│  (Oscuro)           (Claro)     │
│                                 │
└─────────────────────────────────┘
```

**Dark Theme** 🌙
- Fondo oscuro (#1e1e2e)
- Texto blanco
- Ideal para trabajo nocturno
- Reduce fatiga visual

**Light Theme** ☀️
- Fondo claro (#f5f5f5)
- Texto oscuro
- Máxima legibilidad
- Ideal para ambientes luminosos

---

## 💾 CORREGIDO: Montar como Disco

### ⚠️ Requisito: WinFsp (YA INSTALADO ✅)

```
Tab: "Montar Disco"

┌─────────────────────────────────────┐
│  Configuración de Montaje           │
│                                     │
│  Letra de Unidad:  [W: ▼]           │
│  ├─ W:                              │
│  ├─ X:                              │
│  ├─ Y:                              │
│  └─ Z:                              │
│                                     │
│  Seleccionar Bucket: [mi-bucket ▼]  │
│                                     │
│  Estado: No montado                 │
│                                     │
│  [🔗 Montar Unidad]                 │
│  [📤 Desmontar Unidad]              │
│                                     │
└─────────────────────────────────────┘
```

### Pasos:
1. **Selecciona letra**: W:, X:, Y:, o Z:
2. **Selecciona bucket**: De tu lista
3. **Clic en**: 🔗 Montar Unidad
4. **Espera**: 5-10 segundos
5. **Accede**: Desde "Este Equipo" en Windows

### Uso del Disco Montado:
```
Este Equipo
├─ 💿 Disco Local (C:)
├─ 💿 Datos (D:)
└─ 🌐 Vultr-Mi-Perfil (W:)  ← Tu storage montado
    ├─ 📁 carpeta1
    ├─ 📁 carpeta2
    ├─ 📄 archivo1.pdf
    └─ 📄 foto.jpg
```

Puedes:
- ✅ Abrir archivos directamente
- ✅ Copiar/pegar archivos
- ✅ Arrastrar y soltar
- ✅ Usar con cualquier programa

---

## 📦 Gestión de Buckets

### Tab: "Principal"

```
┌─────────────────────────────────────┐
│  📦 Crear Bucket                    │
│  ┌─────────────────────┐            │
│  │ nombre-del-bucket   │ [Crear]    │
│  └─────────────────────┘            │
│                                     │
│  📋 Buckets Existentes              │
│  [mi-bucket ▼]                      │
│                                     │
│  📁 Contenido:                      │
│  ├─ 📁 carpeta1/                    │
│  ├─ 📁 carpeta2/                    │
│  ├─ 📄 documento.pdf                │
│  └─ 🖼️ imagen.jpg                   │
│                                     │
│  [📤 Subir Archivo]                 │
│  [📁 Subir Carpeta]                 │
│  [💾 Descargar]                     │
│  [🗑️ Eliminar]                      │
│                                     │
└─────────────────────────────────────┘
```

---

## ⚡ Sincronización en Tiempo Real

### Tab: "Sincronización en Tiempo Real"

```
┌─────────────────────────────────────┐
│  📁 Carpeta a Monitorear            │
│  ┌─────────────────────────────┐    │
│  │ C:\Users\...\MiCarpeta      │    │
│  └─────────────────────────────┘    │
│  [📁 Seleccionar Carpeta]           │
│                                     │
│  Estado: ⏹️ Detenido                │
│                                     │
│  [▶️ Iniciar Sincronización]        │
│  [⏹️ Detener Sincronización]        │
│                                     │
│  📊 Actividad:                      │
│  ┌─────────────────────────────┐    │
│  │ ✅ archivo.txt subido        │    │
│  │ ✅ foto.jpg subida           │    │
│  │ ⚠️ Esperando cambios...      │    │
│  └─────────────────────────────┘    │
│                                     │
└─────────────────────────────────────┘
```

### Cómo funciona:
1. **Selecciona carpeta** a sincronizar
2. **Inicia sincronización**
3. **Cualquier cambio** se sube automáticamente:
   - ✅ Archivos nuevos
   - ✅ Archivos modificados
   - ✅ Archivos eliminados

---

## 💾 Backup Completo

### Tab: "Avanzado"

```
┌─────────────────────────────────────┐
│  💾 Backup Completo                 │
│                                     │
│  Carpeta Origen:                    │
│  [C:\Users\...\Documentos     ]     │
│  [📁 Seleccionar Carpeta]           │
│                                     │
│  Bucket Destino:                    │
│  [backups ▼]                        │
│                                     │
│  [💾 Hacer Backup Completo]         │
│                                     │
│  Progreso:                          │
│  ████████████░░░░░░░ 65%           │
│  Subiendo: foto123.jpg              │
│  12 de 20 archivos                  │
│                                     │
└─────────────────────────────────────┘
```

### Características:
- ✅ Preserva estructura de carpetas
- ✅ Sube todo recursivamente
- ✅ Barra de progreso en tiempo real
- ✅ Contador de archivos

---

## 🔧 Configuración de Perfiles

### Ventana: "Configuración"

```
┌─────────────────────────────────────┐
│  👤 Gestión de Perfiles             │
│                                     │
│  Perfiles Existentes:               │
│  ┌─────────────────────────────┐    │
│  │ ✓ cuenta-personal           │    │
│  │   cuenta-trabajo            │    │
│  │   cuenta-cliente1           │    │
│  └─────────────────────────────┘    │
│                                     │
│  [➕ Agregar Perfil]                │
│  [✏️ Editar Perfil]                 │
│  [🗑️ Eliminar Perfil]               │
│                                     │
└─────────────────────────────────────┘

Agregar Nuevo Perfil:
┌─────────────────────────────────────┐
│  Nombre del Perfil:                 │
│  ┌─────────────────────────────┐    │
│  │ mi-cuenta-vultr             │    │
│  └─────────────────────────────┘    │
│                                     │
│  Access Key:                        │
│  ┌─────────────────────────────┐    │
│  │ ABC123XYZ...                │    │
│  └─────────────────────────────┘    │
│                                     │
│  Secret Key:                        │
│  ┌─────────────────────────────┐    │
│  │ ••••••••••••••••            │    │
│  └─────────────────────────────┘    │
│                                     │
│  Host Base:                         │
│  ┌─────────────────────────────┐    │
│  │ ewr1.vultrobjects.com       │    │
│  └─────────────────────────────┘    │
│                                     │
│  Región:                            │
│  ┌─────────────────────────────┐    │
│  │ ewr1                        │    │
│  └─────────────────────────────┘    │
│                                     │
│  [💾 Guardar]  [❌ Cancelar]        │
└─────────────────────────────────────┘
```

---

## 🎯 Flujo de Trabajo Típico

### Escenario 1: Subir Archivos de Proyecto
```
1. Abrir VultrDriveDesktop
2. Tab "Principal"
3. Seleccionar bucket o crear uno nuevo
4. Clic en "📁 Subir Carpeta"
5. Seleccionar carpeta del proyecto
6. Esperar a que termine
7. ✅ Archivos en la nube
```

### Escenario 2: Sincronizar Documentos
```
1. Abrir VultrDriveDesktop
2. Tab "Sincronización en Tiempo Real"
3. Seleccionar carpeta "Documentos"
4. Clic en "▶️ Iniciar Sincronización"
5. Trabajar normalmente en tus archivos
6. ✅ Cambios se suben automáticamente
```

### Escenario 3: Acceder como Disco
```
1. Abrir VultrDriveDesktop
2. Tab "Montar Disco"
3. Seleccionar letra "W:"
4. Seleccionar bucket
5. Clic en "🔗 Montar Unidad"
6. Abrir "Este Equipo"
7. ✅ Trabajar con archivos como disco local
```

---

## ⚠️ Solución Rápida de Problemas

### Error: "WinFsp no instalado"
```powershell
# Ya está resuelto - WinFsp está instalado ✅
# Si reaparece:
.\instalar_winfsp.ps1
```

### Error: "Python no encontrado"
```powershell
# Usar el acceso directo del escritorio
# O ejecutar:
py app.py
```

### Error: "No se puede conectar"
```
Verificar:
1. ✅ Credenciales correctas (Access Key, Secret Key)
2. ✅ Host Base correcto (ejemplo: ewr1.vultrobjects.com)
3. ✅ Internet conectado
4. ✅ Object Storage habilitado en Vultr
```

---

## 🚀 Tips y Trucos

### 💡 Tip 1: Múltiples Perfiles
Crea perfiles separados para:
- 🏢 Trabajo
- 👤 Personal
- 👥 Clientes

### 💡 Tip 2: Organización de Buckets
```
proyectos/
├─ proyecto-a/
├─ proyecto-b/
└─ proyecto-c/

backups/
├─ 2025-11/
├─ 2025-10/
└─ 2025-09/

documentos/
├─ personal/
├─ trabajo/
└─ compartidos/
```

### 💡 Tip 3: Sincronización Selectiva
Solo sincroniza carpetas importantes:
- ✅ Documentos activos
- ❌ NO sincronices archivos temporales
- ❌ NO sincronices carpetas enormes

### 💡 Tip 4: Montaje para Colaboración
Monta un bucket compartido:
- Equipo accede a los mismos archivos
- Cambios visibles en tiempo real
- Sin necesidad de descargar/subir manualmente

---

## 🎓 Atajos de Teclado (Próximamente)

Actualmente todos los controles se usan con mouse/clic.

En futuras versiones:
- `Ctrl+U` - Subir archivo
- `Ctrl+D` - Descargar
- `Ctrl+N` - Nuevo bucket
- `Ctrl+M` - Montar unidad
- `Ctrl+,` - Configuración

---

## 📞 ¿Necesitas Ayuda?

### Diagnóstico Automático
```powershell
.\verificar.ps1
```

### Documentación Completa
- `README_COMPLETO.md` - Guía completa
- `SOLUCION_MONTAJE.md` - Problemas de montaje
- `PROYECTO_COMPLETADO.md` - Resumen técnico

### Verificar WinFsp
```powershell
.\verificar_winfsp.ps1
```

---

## 🎉 ¡Disfruta VultrDriveDesktop v2.0!

**Todo está listo para usar**:
- ✅ Multiidioma (ES/EN/FR)
- ✅ Temas (Dark/Light)
- ✅ Montaje corregido
- ✅ WinFsp instalado
- ✅ Sin errores

**¡Empieza a usarlo ahora!** 🚀

---

**Última actualización**: 6 de noviembre de 2025
**Versión**: 2.0
