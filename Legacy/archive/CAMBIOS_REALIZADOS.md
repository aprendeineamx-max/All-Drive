# 🔧 Cambios Realizados - Desmontar Específico por Letra

## ✅ Problemas Solucionados

### 1. **Botón Naranja (Desmontar Específico) - Ahora Solo Desmonta ESA Letra**
- **Problema**: Al hacer clic en el botón naranja para desmontar la letra V, se desmontaban TODAS las unidades
- **Solución**: 
  - `unmount_drive()` en `drive_detector.py` usa `net use {letter}: /delete` (específico)
  - `unmount_drive()` en `rclone_manager.py` también usa `net use` (específico)
  - Ya NO mata todos los procesos rclone con `taskkill /IM rclone.exe`

### 2. **Botón "Desmontar Unidad" - Ahora Funciona Correctamente**
- **Problema**: El botón azul no desmontaba la unidad seleccionada
- **Solución**:
  - Mejorado el método `unmount_drive()` en `main_window.py`
  - Usa correctamente `self.rclone_manager.unmount_drive(drive_letter)`
  - Solo desmonta la letra seleccionada en el ComboBox

### 3. **Sincronización Automática de Botones al Cambiar Letra**
- **Problema**: Al cambiar de letra en "Configuración de Montaje", los botones no se actualizaban
- **Solución**:
  - ComboBox conectado a `update_unmount_button_state()` (línea 432)
  - Cuando cambias letra → se verifica automáticamente si está montada
  - Si está montada → botón azul HABILITADO (puedes desmontar)
  - Si NO está montada → botón azul DESHABILITADO (gris)

## 📋 Cambios de Código

### `drive_detector.py`
```python
@staticmethod
def unmount_drive(drive_letter: str) -> Tuple[bool, str]:
    """Desmonta SOLO una unidad específica (sin afectar las demás)"""
    # Estrategia: Usar 'net use' para desmontar SOLO esa letra
    result = subprocess.run(
        ['net', 'use', drive_path, '/delete', '/yes'],
        capture_output=True,
        text=True
    )
    # Esto NO afecta las demás unidades montadas
```

### `rclone_manager.py`
```python
def unmount_drive(self, drive_letter):
    """Unmount the drive usando net use (específico para esa letra)"""
    # Primero intentar con net use para desmontar SOLO esa letra
    result = subprocess.run(
        ['net', 'use', drive_path, '/delete', '/yes'],
        capture_output=True,
        text=True
    )
```

### `ui/main_window.py`
```python
def unmount_drive(self):
    """Desmonta SOLO la unidad seleccionada (sin afectar las demás)"""
    drive_letter = self.drive_letter_input.currentText()
    success, message = self.rclone_manager.unmount_drive(drive_letter)
    
    if success:
        # Refrescar después de 2 segundos
        QTimer.singleShot(2000, self.detect_mounted_drives)
        QTimer.singleShot(2000, self.update_unmount_button_state)

def update_unmount_button_state(self):
    """Verifica si la letra seleccionada está montada"""
    selected_letter = self.drive_letter_input.currentText()
    detected_drives = DriveDetector.detect_mounted_drives()
    mounted_letters = [d['letter'] for d in detected_drives]
    
    if selected_letter in mounted_letters:
        # ✅ MONTADA: botón azul habilitado
        self.unmount_button.setEnabled(True)
        self.mount_button.setEnabled(False)
    else:
        # ⭕ NO MONTADA: botón azul deshabilitado
        self.unmount_button.setEnabled(False)
        self.mount_button.setEnabled(True)
```

## 🧪 Cómo Verificar

1. **Monta varias unidades** (ej: V:, W:, Y:)
2. **Click en botón naranja para desmontar V:** 
   - ✅ Se desmonta SOLO V
   - ✅ W y Y permanecen montadas
3. **En "Configuración de Montaje", selecciona W:**
   - ✅ Botón "Desmontar Unidad" se habilita (azul)
   - ✅ Muestra "✅ Unidad W: está montada"
4. **Cambias a letra disponible (ej: Z):**
   - ✅ Botón "Desmontar Unidad" se deshabilita (gris)
   - ✅ Muestra "⭕ Unidad Z: no está montada"
5. **Click en "Desmontar Unidad" cuando W está seleccionada:**
   - ✅ Se desmonta SOLO W
   - ✅ Las demás permanecen montadas

## 🎯 Beneficios

- ✅ Mejor control: desmontar unidades específicas sin afectar otras
- ✅ Mayor seguridad: no pierdes datos de otras unidades al desmontar una
- ✅ Interfaz intuitiva: los botones se actualizan automáticamente
- ✅ Sincronización perfecta: la UI siempre refleja el estado real
