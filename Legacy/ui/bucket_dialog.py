from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLineEdit, QPushButton, 
                             QLabel, QMessageBox, QHBoxLayout, QTextEdit)
from PyQt6.QtCore import Qt

class BucketDialog(QDialog):
    """Diálogo para crear nuevos buckets en Vultr Object Storage"""
    
    def __init__(self, parent=None, translations=None):
        super().__init__(parent)
        self.translations = translations
        
        self.setWindowTitle("Crear Nuevo Bucket")
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
        title_label = QLabel("➕ Crear Nuevo Bucket")
        title_label.setStyleSheet("font-size: 14pt; font-weight: bold; color: #3498db;")
        layout.addWidget(title_label)
        
        # Campo de nombre
        layout.addWidget(QLabel("Nombre del Bucket:"))
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("mi-bucket-ejemplo")
        self.name_input.textChanged.connect(self.on_name_changed)
        layout.addWidget(self.name_input)
        
        # Preview del nombre (se actualiza en tiempo real)
        self.preview_label = QLabel("")
        self.preview_label.setStyleSheet("color: #7f8c8d; font-size: 9pt; font-style: italic;")
        layout.addWidget(self.preview_label)
        
        # Información de ayuda
        help_text = QTextEdit()
        help_text.setReadOnly(True)
        help_text.setMaximumHeight(140)
        help_text.setPlainText(
            "📋 Reglas de nombre para buckets S3:\n\n"
            "✅ Solo minúsculas (a-z), números (0-9) y guiones (-)\n"
            "✅ Entre 3 y 63 caracteres\n"
            "✅ Debe empezar y terminar con letra o número\n"
            "❌ No puede contener guiones consecutivos (--)\n"
            "❌ No puede ser una dirección IP\n\n"
            "💡 Ejemplos válidos: mi-bucket, data-2024, backups-abc"
        )
        help_text.setStyleSheet(
            "background-color: #ecf0f1; "
            "border: 1px solid #bdc3c7; "
            "border-radius: 5px; "
            "padding: 10px; "
            "font-size: 10pt;"
        )
        layout.addWidget(help_text)
        
        # Advertencia de costos
        warning_label = QLabel(
            "⚠️  Crear buckets es gratis, pero el almacenamiento se cobra por GB/mes"
        )
        warning_label.setStyleSheet(
            "color: #e67e22; "
            "font-weight: bold; "
            "font-size: 9pt; "
            "padding: 10px; "
            "background-color: #fef5e7; "
            "border-left: 4px solid #e67e22; "
            "border-radius: 3px;"
        )
        warning_label.setWordWrap(True)
        layout.addWidget(warning_label)
        
        # Botones
        buttons_layout = QHBoxLayout()
        
        self.create_btn = QPushButton("➕ Crear Bucket")
        self.create_btn.clicked.connect(self.validate_and_accept)
        self.create_btn.setEnabled(False)  # Deshabilitado hasta que el nombre sea válido
        self.create_btn.setStyleSheet("""
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
            QPushButton:disabled {
                background-color: #95a5a6;
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
        buttons_layout.addWidget(self.create_btn)
        layout.addLayout(buttons_layout)
        
        self.setLayout(layout)
    
    def on_name_changed(self, text):
        """Validar nombre en tiempo real"""
        # Convertir a minúsculas automáticamente
        lowercase_text = text.lower()
        if text != lowercase_text:
            self.name_input.blockSignals(True)
            cursor_pos = self.name_input.cursorPosition()
            self.name_input.setText(lowercase_text)
            self.name_input.setCursorPosition(cursor_pos)
            self.name_input.blockSignals(False)
        
        # Validar
        is_valid = self._validate_bucket_name(lowercase_text)
        
        if lowercase_text:
            if is_valid:
                self.preview_label.setText("✅ Nombre válido")
                self.preview_label.setStyleSheet("color: #27ae60; font-weight: bold;")
                self.create_btn.setEnabled(True)
            else:
                self.preview_label.setText("❌ Nombre inválido (revisa las reglas)")
                self.preview_label.setStyleSheet("color: #e74c3c; font-weight: bold;")
                self.create_btn.setEnabled(False)
        else:
            self.preview_label.setText("")
            self.create_btn.setEnabled(False)
    
    def _validate_bucket_name(self, name):
        """Validar nombre de bucket (reglas S3)"""
        import re
        
        if not name:
            return False
        
        # Longitud: 3-63 caracteres
        if len(name) < 3 or len(name) > 63:
            return False
        
        # Solo minúsculas, números y guiones
        # Debe empezar y terminar con letra o número
        if not re.match(r'^[a-z0-9][a-z0-9-]*[a-z0-9]$', name):
            # Caso especial: nombre de 3 caracteres sin guiones
            if len(name) == 3 and re.match(r'^[a-z0-9]+$', name):
                return True
            return False
        
        # No puede tener guiones consecutivos
        if '--' in name:
            return False
        
        # No puede ser una IP
        if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', name):
            return False
        
        return True
    
    def validate_and_accept(self):
        """Validar antes de crear"""
        bucket_name = self.name_input.text().strip().lower()
        
        if not bucket_name:
            QMessageBox.warning(self, "Error", "El nombre del bucket no puede estar vacío")
            return
        
        if not self._validate_bucket_name(bucket_name):
            QMessageBox.warning(
                self,
                "Error",
                "El nombre del bucket no cumple con las reglas de S3.\n\n"
                "Consulta la sección de ayuda para más información."
            )
            return
        
        self.accept()
    
    def get_bucket_name(self):
        """Obtener nombre del bucket"""
        return self.name_input.text().strip().lower()
