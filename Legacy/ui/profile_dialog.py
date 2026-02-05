from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLineEdit, QPushButton, 
                             QLabel, QMessageBox, QHBoxLayout, QCheckBox)
from PyQt6.QtCore import Qt

class ProfileDialog(QDialog):
    """Diálogo para crear o editar perfiles de Vultr Object Storage"""
    
    def __init__(self, parent=None, profile_data=None, translations=None):
        super().__init__(parent)
        self.translations = translations
        self.profile_data = profile_data
        self.is_edit_mode = profile_data is not None
        
        self.setWindowTitle(
            "Editar Perfil" if self.is_edit_mode else "Crear Nuevo Perfil"
        )
        self.setModal(True)
        self.setMinimumWidth(500)
        
        self.setup_ui()
    
    def tr(self, key, *args):
        """Traducir texto"""
        if self.translations:
            return self.translations.get(key, *args)
        return key
    
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Título
        title_label = QLabel(
            "✏️ Editar Perfil" if self.is_edit_mode else "➕ Crear Nuevo Perfil"
        )
        title_label.setStyleSheet("font-size: 14pt; font-weight: bold; color: #3498db;")
        layout.addWidget(title_label)
        
        # Campo: Nombre del Perfil
        layout.addWidget(QLabel("Nombre del Perfil:"))
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Ej: Dolphin-1000, Mi-Storage-Premium")
        if self.profile_data:
            self.name_input.setText(self.profile_data.get('name', ''))
            self.name_input.setReadOnly(True)  # No editable en modo edición
            self.name_input.setStyleSheet("background-color: #ecf0f1;")
        layout.addWidget(self.name_input)
        
        # Campo: Access Key
        layout.addWidget(QLabel("Access Key (Vultr):"))
        self.access_key_input = QLineEdit()
        self.access_key_input.setPlaceholderText("TO5MI6UX2KIIMWIBIWBSS5XKFXO5YFDJGOAQ")
        if self.profile_data:
            self.access_key_input.setText(self.profile_data.get('access_key', ''))
        layout.addWidget(self.access_key_input)
        
        # Campo: Secret Key
        layout.addWidget(QLabel("Secret Key (Vultr):"))
        self.secret_key_container = QVBoxLayout()
        self.secret_key_input = QLineEdit()
        self.secret_key_input.setPlaceholderText("••••••••••••••••••••")
        self.secret_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        if self.profile_data:
            self.secret_key_input.setText(self.profile_data.get('secret_key', ''))
        
        # Checkbox para mostrar/ocultar secret key
        self.show_secret_checkbox = QCheckBox("Mostrar Secret Key")
        self.show_secret_checkbox.stateChanged.connect(self.toggle_secret_visibility)
        
        self.secret_key_container.addWidget(self.secret_key_input)
        self.secret_key_container.addWidget(self.show_secret_checkbox)
        layout.addLayout(self.secret_key_container)
        
        # Campo: Host Base
        layout.addWidget(QLabel("Host Base (Endpoint):"))
        self.host_base_input = QLineEdit()
        self.host_base_input.setPlaceholderText("sjc1.vultrobjects.com o ewr1.vultrobjects.com")
        if self.profile_data:
            self.host_base_input.setText(self.profile_data.get('host_base', ''))
        layout.addWidget(self.host_base_input)
        
        # Ayuda
        help_text = QLabel(
            "ℹ️ Puedes encontrar estas credenciales en:\n"
            "Vultr Dashboard → Object Storage → Credenciales"
        )
        help_text.setStyleSheet("color: #7f8c8d; font-size: 9pt; margin-top: 10px;")
        help_text.setWordWrap(True)
        layout.addWidget(help_text)
        
        # Botones
        buttons_layout = QHBoxLayout()
        
        self.save_btn = QPushButton("💾 Guardar" if self.is_edit_mode else "➕ Crear Perfil")
        self.save_btn.clicked.connect(self.validate_and_accept)
        self.save_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                font-weight: bold;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 11pt;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        
        self.cancel_btn = QPushButton("❌ Cancelar")
        self.cancel_btn.clicked.connect(self.reject)
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                font-weight: bold;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 11pt;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        
        buttons_layout.addWidget(self.cancel_btn)
        buttons_layout.addWidget(self.save_btn)
        layout.addLayout(buttons_layout)
        
        self.setLayout(layout)
    
    def toggle_secret_visibility(self, state):
        """Alternar visibilidad de la Secret Key"""
        if state == Qt.CheckState.Checked.value:
            self.secret_key_input.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            self.secret_key_input.setEchoMode(QLineEdit.EchoMode.Password)
    
    def validate_and_accept(self):
        """Validar datos antes de aceptar"""
        name = self.name_input.text().strip()
        access_key = self.access_key_input.text().strip()
        secret_key = self.secret_key_input.text().strip()
        host_base = self.host_base_input.text().strip()
        
        # Validaciones
        if not name:
            QMessageBox.warning(self, "Error", "El nombre del perfil es obligatorio")
            self.name_input.setFocus()
            return
        
        if not access_key:
            QMessageBox.warning(self, "Error", "El Access Key es obligatorio")
            self.access_key_input.setFocus()
            return
        
        if not secret_key:
            QMessageBox.warning(self, "Error", "El Secret Key es obligatorio")
            self.secret_key_input.setFocus()
            return
        
        if not host_base:
            QMessageBox.warning(self, "Error", "El Host Base es obligatorio")
            self.host_base_input.setFocus()
            return
        
        # Validar formato de host_base (debe ser un dominio)
        if ' ' in host_base or not '.' in host_base:
            QMessageBox.warning(
                self,
                "Error",
                "El Host Base debe ser un dominio válido\n"
                "Ejemplo: sjc1.vultrobjects.com"
            )
            self.host_base_input.setFocus()
            return
        
        self.accept()
    
    def get_profile_data(self):
        """Obtener datos del perfil"""
        return {
            'name': self.name_input.text().strip(),
            'access_key': self.access_key_input.text().strip(),
            'secret_key': self.secret_key_input.text().strip(),
            'host_base': self.host_base_input.text().strip()
        }
