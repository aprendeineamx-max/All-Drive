from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QListWidget, QFormLayout, 
    QLineEdit, QSpinBox, QComboBox, QPushButton, QMessageBox, 
    QGroupBox, QScrollArea, QWidget, QLabel, QInputDialog
)
from PyQt6.QtCore import Qt

class PlanEditorDialog(QDialog):
    def __init__(self, config_manager, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.setWindowTitle("Editor de Planes de Rendimiento")
        self.resize(900, 600)
        
        self.current_plan_name = None
        self.is_modified = False
        
        self.base_defaults = {
            "transfers": "320", "checkers": "320", "tpslimit": "0", "burst": "0",
            "vfs_cache_mode": "writes", "buffer_size": "64M", 
            "vfs_read_chunk_size": "128M", "vfs_write_back": "5s",
            "timeout": "10h", "retries": "5"
        }

        self.init_ui()
        self.load_plans()

    def init_ui(self):
        main_layout = QHBoxLayout(self)

        # === PANEL IZQUIERDO: LISTA DE PLANES ===
        left_layout = QVBoxLayout()
        left_layout.addWidget(QLabel("📂 Planes Disponibles"))
        
        self.plan_list = QListWidget()
        self.plan_list.currentItemChanged.connect(self.on_plan_selected)
        left_layout.addWidget(self.plan_list)

        # Botones de gestión
        btn_layout = QHBoxLayout()
        self.btn_new = QPushButton("➕ Nuevo")
        self.btn_new.clicked.connect(self.create_plan)
        self.btn_delete = QPushButton("🗑️ Eliminar")
        self.btn_delete.clicked.connect(self.delete_plan)
        btn_layout.addWidget(self.btn_new)
        btn_layout.addWidget(self.btn_delete)
        left_layout.addLayout(btn_layout)
        
        main_layout.addLayout(left_layout, 1)

        # === PANEL DERECHO: FORMULARIO DE EDICIÓN ===
        right_container = QGroupBox("⚙️ Configuración del Plan")
        right_layout = QVBoxLayout(right_container)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        form_widget = QWidget()
        self.form_layout = QVBoxLayout(form_widget)
        
        # 1. Grupo Transferencia
        g_trans = QGroupBox("🚀 Rendimiento de Transferencia (Sync/Upload)")
        f_trans = QFormLayout()
        
        self.inp_name = QLineEdit()
        self.inp_name.setPlaceholderText("Nombre del Plan")
        f_trans.addRow("Nombre:", self.inp_name)
        
        self.inp_transfers = QSpinBox()
        self.inp_transfers.setRange(1, 2000)
        f_trans.addRow("Transfers (Hilos):", self.inp_transfers)
        
        self.inp_checkers = QSpinBox()
        self.inp_checkers.setRange(1, 2000)
        f_trans.addRow("Checkers:", self.inp_checkers)
        
        self.inp_tps = QSpinBox()
        self.inp_tps.setRange(0, 1000)
        self.inp_tps.setSpecialValueText("Ilimitado")
        f_trans.addRow("TPS Limit:", self.inp_tps)
        
        self.inp_burst = QSpinBox()
        self.inp_burst.setRange(0, 1000)
        f_trans.addRow("Burst Limit:", self.inp_burst)
        
        g_trans.setLayout(f_trans)
        self.form_layout.addWidget(g_trans)

        # 2. Grupo Montaje (VFS)
        g_vfs = QGroupBox("💾 Montaje de Unidad (VFS Cache)")
        f_vfs = QFormLayout()
        
        self.cmb_cache_mode = QComboBox()
        self.cmb_cache_mode.addItems(["off", "minimal", "writes", "full"])
        f_vfs.addRow("Cache Mode:", self.cmb_cache_mode)
        
        self.inp_buffer = QLineEdit()
        self.inp_buffer.setPlaceholderText("Ej: 64M")
        f_vfs.addRow("Buffer Size:", self.inp_buffer)
        
        self.inp_chunk = QLineEdit()
        self.inp_chunk.setPlaceholderText("Ej: 128M")
        f_vfs.addRow("Read Chunk Size:", self.inp_chunk)
        
        self.inp_writeback = QLineEdit()
        self.inp_writeback.setPlaceholderText("Ej: 5s")
        f_vfs.addRow("Write Back Time:", self.inp_writeback)
        
        g_vfs.setLayout(f_vfs)
        self.form_layout.addWidget(g_vfs)
        
        # 3. Grupo Red
        g_net = QGroupBox("🌐 Red y Estabilidad")
        f_net = QFormLayout()
        
        self.inp_timeout = QLineEdit()
        self.inp_timeout.setPlaceholderText("Ej: 10h")
        f_net.addRow("Timeout:", self.inp_timeout)
        
        self.inp_retries = QSpinBox()
        self.inp_retries.setRange(1, 100)
        f_net.addRow("Retries:", self.inp_retries)
        
        g_net.setLayout(f_net)
        self.form_layout.addWidget(g_net)

        scroll.setWidget(form_widget)
        right_layout.addWidget(scroll)

        # Botones de Acción
        action_layout = QHBoxLayout()
        self.btn_save = QPushButton("💾 Guardar Cambios")
        self.btn_save.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold; padding: 8px;")
        self.btn_save.clicked.connect(self.save_current_plan)
        
        self.btn_restore = QPushButton("🔄 Restaurar Valores")
        self.btn_restore.clicked.connect(self.restore_values)
        
        action_layout.addWidget(self.btn_restore)
        action_layout.addStretch()
        action_layout.addWidget(self.btn_save)
        right_layout.addLayout(action_layout)

        main_layout.addWidget(right_container, 2)

    def load_plans(self):
        self.plan_list.clear()
        plans = self.config_manager.get_plans()
        for name in plans:
            self.plan_list.addItem(name)
        
        # Seleccionar plan activo si existe
        active = self.config_manager.get_active_plan()
        items = self.plan_list.findItems(active, Qt.MatchFlag.MatchExactly)
        if items:
            self.plan_list.setCurrentItem(items[0])
        elif self.plan_list.count() > 0:
            self.plan_list.setCurrentRow(0)

    def on_plan_selected(self, current, previous):
        if not current:
            return
        
        plan_name = current.text()
        self.current_plan_name = plan_name
        self.inp_name.setText(plan_name)
        
        # Cargar datos
        plan = self.config_manager.get_plan(plan_name) or {}
        
        # Mapear datos a inputs
        self.inp_transfers.setValue(int(plan.get("transfers", 32)))
        self.inp_checkers.setValue(int(plan.get("checkers", 32)))
        self.inp_tps.setValue(int(plan.get("tpslimit", 0)))
        self.inp_burst.setValue(int(plan.get("burst", 0)))
        
        self.cmb_cache_mode.setCurrentText(plan.get("vfs_cache_mode", "writes"))
        self.inp_buffer.setText(str(plan.get("buffer_size", "64M")))
        self.inp_chunk.setText(str(plan.get("vfs_read_chunk_size", "128M")))
        self.inp_writeback.setText(str(plan.get("vfs_write_back", "5s")))
        
        self.inp_timeout.setText(str(plan.get("timeout", "10h")))
        self.inp_retries.setValue(int(plan.get("retries", 5)))
        
        # Deshabilitar edición de nombre para planes por defecto? Opcional. 
        # Permitimos todo por ahora para máxima flexibilidad.

    def create_plan(self):
        name, ok = QInputDialog.getText(self, "Nuevo Plan", "Nombre del Plan:")
        if ok and name:
            if self.config_manager.get_plan(name):
                QMessageBox.warning(self, "Error", "Ya existe un plan con ese nombre.")
                return
            
            # Crear con defaults base
            self.config_manager.save_plan(name, self.base_defaults.copy())
            self.load_plans()
            
            # Seleccionar nuevo
            items = self.plan_list.findItems(name, Qt.MatchFlag.MatchExactly)
            if items:
                self.plan_list.setCurrentItem(items[0])

    def delete_plan(self, name=None):
        if not self.current_plan_name:
            return
            
        confirm = QMessageBox.question(
            self, "Confirmar Eliminar", 
            f"¿Eliminar el plan '{self.current_plan_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if confirm == QMessageBox.StandardButton.Yes:
            self.config_manager.delete_plan(self.current_plan_name)
            self.load_plans()

    def save_current_plan(self):
        if not self.current_plan_name:
            return
            
        new_name = self.inp_name.text().strip()
        if not new_name:
            QMessageBox.warning(self, "Error", "El nombre no puede estar vacío")
            return

        # Si cambió el nombre, verificar unicidad
        if new_name != self.current_plan_name:
            if self.config_manager.get_plan(new_name):
                 QMessageBox.warning(self, "Error", "Ya existe otro plan con ese nombre.")
                 return
            # Eliminar viejo y crear nuevo es la forma más facil de renombrar
            self.config_manager.delete_plan(self.current_plan_name)
            self.current_plan_name = new_name # Actualizar referencia

        config = {
            "transfers": str(self.inp_transfers.value()),
            "checkers": str(self.inp_checkers.value()),
            "tpslimit": str(self.inp_tps.value()),
            "burst": str(self.inp_burst.value()),
            "vfs_cache_mode": self.cmb_cache_mode.currentText(),
            "buffer_size": self.inp_buffer.text(),
            "vfs_read_chunk_size": self.inp_chunk.text(),
            "vfs_write_back": self.inp_writeback.text(),
            "timeout": self.inp_timeout.text(),
            "retries": str(self.inp_retries.value())
        }
        
        self.config_manager.save_plan(self.current_plan_name, config)
        QMessageBox.information(self, "Guardado", "Plan actualizado correctamente.")
        self.load_plans() # Refrescar lista por si cambió nombre

    def restore_values(self):
        # Recargar desde disco (deshacer cambios no guardados)
        if self.current_plan_name:
            # Trigger reload
            dummy = None
            self.on_plan_selected(self.plan_list.currentItem(), dummy)
