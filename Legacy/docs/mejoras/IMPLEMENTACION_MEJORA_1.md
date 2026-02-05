# 🚀 Implementación: Mejora #1 - Múltiples Buckets Simultáneos

## 📋 Plan de Implementación

### **Estado Actual**
- Solo se puede montar un bucket a la vez
- Una letra de unidad activa
- No hay persistencia de múltiples montajes

### **Estado Deseado**
- Montar múltiples buckets simultáneamente
- Cada uno en diferente letra (V:, W:, X:, etc.)
- Panel visual con lista de buckets montados
- Montar/desmontar individual
- Guardar configuración de múltiples montajes

---

## 🔧 Cambios Necesarios

### **1. Estructura de Datos Nueva**
```python
# Gestor de múltiples montajes
mounted_drives = {
    'V': {
        'profile': 'cuenta-trabajo',
        'bucket': 'proyecto-alpha',
        'process': <subprocess>,
        'status': 'connected',
        'mounted_at': <timestamp>
    },
    'W': {
        'profile': 'cuenta-personal',
        'bucket': 'fotos-familia',
        'process': <subprocess>,
        'status': 'connected',
        'mounted_at': <timestamp>
    }
}
```

### **2. Modificaciones en RcloneManager**
- ✅ Método para montar múltiples buckets
- ✅ Tracking de procesos por letra de unidad
- ✅ Método para obtener estado de cada montaje
- ✅ Desmontar individualmente

### **3. Modificaciones en MainWindow**
- ✅ Nuevo widget: ListaMontajesWidget
- ✅ Tabla/Lista de buckets montados
- ✅ Botones: Montar Nuevo, Desmontar, Abrir
- ✅ Indicadores de estado visual
- ✅ Actualización en tiempo real

### **4. Persistencia**
- ✅ Guardar lista de montajes en config
- ✅ Auto-montar al iniciar (opcional)
- ✅ Recordar última configuración

---

## 📝 Archivos a Modificar

1. **`rclone_manager.py`**
   - Clase `MultipleMountManager`
   - Gestión de múltiples procesos
   - Estado de cada montaje

2. **`ui/main_window.py`**
   - Widget de lista de montajes
   - Botones de gestión
   - Actualización de UI

3. **`config_manager.py`**
   - Guardar/cargar múltiples montajes
   - Configuración de auto-montaje

4. **`ui/mount_list_widget.py`** (NUEVO)
   - Widget especializado para lista
   - Cada fila: estado, letra, bucket, acciones

---

## 🎨 Diseño de UI

```
┌─────────────────────────────────────────────┐
│  📊 Unidades Montadas                       │
├─────────────────────────────────────────────┤
│                                             │
│  ┌───────────────────────────────────────┐ │
│  │ V:  ✓  proyecto-alpha   [🗑][📂]     │ │
│  │     cuenta-trabajo                     │ │
│  ├───────────────────────────────────────┤ │
│  │ W:  ✓  fotos-familia    [🗑][📂]     │ │
│  │     cuenta-personal                    │ │
│  ├───────────────────────────────────────┤ │
│  │ X:  ⏸  backup-mensual   [▶][🗑][📂]  │ │
│  │     cuenta-trabajo     (Desconectado) │ │
│  └───────────────────────────────────────┘ │
│                                             │
│  [➕ Montar Nuevo Bucket]  [🗑 Desmontar Todos] │
│                                             │
└─────────────────────────────────────────────┘
```

---

## 🏗️ Implementación Paso a Paso

### **Paso 1: Crear MultipleMountManager**
```python
class MultipleMountManager:
    def __init__(self, rclone_manager):
        self.rclone_manager = rclone_manager
        self.mounted_drives = {}  # {letra: info_montaje}
        
    def mount_drive(self, letter, profile, bucket):
        # Montar nuevo bucket
        pass
        
    def unmount_drive(self, letter):
        # Desmontar específico
        pass
        
    def get_all_mounted(self):
        # Obtener lista de montados
        pass
        
    def get_status(self, letter):
        # Estado de una unidad
        pass
```

### **Paso 2: Crear MountListWidget**
```python
class MountListWidget(QWidget):
    def __init__(self, mount_manager):
        # Widget personalizado para lista
        # Tabla con columnas: Estado | Letra | Bucket | Perfil | Acciones
        pass
```

### **Paso 3: Integrar en MainWindow**
```python
# En pestaña "Montar Disco"
self.mount_list_widget = MountListWidget(self.multiple_mount_manager)
self.mount_tab_layout.addWidget(self.mount_list_widget)
```

### **Paso 4: Agregar Botones de Gestión**
```python
# Botón para agregar nuevo montaje
btn_mount_new = QPushButton("➕ Montar Nuevo Bucket")
btn_mount_new.clicked.connect(self.show_mount_dialog)

# Botón para desmontar todos
btn_unmount_all = QPushButton("🗑 Desmontar Todos")
btn_unmount_all.clicked.connect(self.unmount_all_drives)
```

### **Paso 5: Diálogo para Nuevo Montaje**
```python
class NewMountDialog(QDialog):
    def __init__(self):
        # Dialog con:
        # - ComboBox de perfiles
        # - ComboBox de buckets
        # - ComboBox de letra de unidad
        # - Botones OK/Cancel
        pass
```

---

## ⏱️ Estimación de Tiempo

| Tarea | Tiempo | Estado |
|-------|--------|--------|
| MultipleMountManager | 2 horas | ⏳ |
| MountListWidget | 2 horas | ⏳ |
| Integración en MainWindow | 1 hora | ⏳ |
| NewMountDialog | 1 hora | ⏳ |
| Persistencia | 1 hora | ⏳ |
| Testing | 1 hora | ⏳ |
| **TOTAL** | **8 horas** | |

---

## 🧪 Plan de Pruebas

1. ✅ Montar 2 buckets simultáneamente
2. ✅ Montar 3+ buckets
3. ✅ Desmontar uno, otros siguen funcionando
4. ✅ Reiniciar app, verificar persistencia
5. ✅ Probar con buckets de diferentes perfiles
6. ✅ Verificar que no haya conflictos de letras
7. ✅ Abrir explorador desde cada montaje

---

## 🚀 Beneficios Esperados

**Antes**:
- 1 bucket montado
- Cambiar = desmontar y remontar
- Incómodo para múltiples proyectos

**Después**:
- N buckets simultáneos
- Cada uno en su letra
- Cambio instantáneo entre proyectos
- Mejor organización

---

## 📊 Métricas de Éxito

- ✅ Soportar al menos 5 montajes simultáneos
- ✅ Cambio entre montajes < 1 segundo
- ✅ Sin errores de conflicto de letras
- ✅ Estado visual claro de cada montaje
- ✅ Persistencia entre sesiones

---

## 🔄 Próximos Pasos

1. Implementar `MultipleMountManager` ← **EMPEZAR AQUÍ**
2. Crear `MountListWidget`
3. Integrar en `MainWindow`
4. Agregar persistencia
5. Testing exhaustivo
6. Documentación

---

¿Procedemos con la implementación? 🚀

