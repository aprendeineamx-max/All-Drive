"""
Content Panel - Panel de contenido principal que cambia según el tipo de almacenamiento

Este widget contiene las pestañas y contenido específico para cada tipo
de almacenamiento seleccionado en la barra lateral.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QLabel,
    QStackedWidget, QGroupBox, QComboBox, QPushButton,
    QScrollArea, QFormLayout, QLineEdit, QListWidget,
    QMessageBox, QFileDialog, QProgressBar, QTextEdit,
    QSizePolicy, QListWidgetItem
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont


class ContentPanel(QWidget):
    """
    Panel principal de contenido que muestra las pestañas y opciones
    según el tipo de almacenamiento seleccionado.
    """
    
    mount_requested = pyqtSignal(str, str)  # account_id, drive_letter
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_storage = None
        self._current_account = None
        self.storage_handlers = {}  # storage_id -> BaseStorage instance
        self.init_ui()
    
    def init_ui(self):
        """Inicializa la interfaz del panel de contenido"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Header con información del tipo de almacenamiento actual
        self.header = QWidget()
        header_layout = QHBoxLayout(self.header)
        header_layout.setContentsMargins(0, 0, 0, 10)
        
        self.storage_icon = QLabel("📁")
        self.storage_icon.setFont(QFont("Segoe UI", 28))
        header_layout.addWidget(self.storage_icon)
        
        header_info = QVBoxLayout()
        self.storage_title = QLabel("Selecciona un almacenamiento")
        self.storage_title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        self.storage_title.setStyleSheet("color: white;")
        
        self.storage_desc = QLabel("Usa la barra lateral para elegir un tipo")
        self.storage_desc.setStyleSheet("color: #7f8c8d;")
        
        header_info.addWidget(self.storage_title)
        header_info.addWidget(self.storage_desc)
        header_layout.addLayout(header_info, 1)
        
        layout.addWidget(self.header)
        
        # Pestañas principales
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #34495e;
                border-radius: 5px;
                background-color: #2c3e50;
            }
            QTabBar::tab {
                background-color: #34495e;
                color: #bdc3c7;
                padding: 10px 20px;
                margin-right: 2px;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
            }
            QTabBar::tab:selected {
                background-color: #2c3e50;
                color: white;
            }
            QTabBar::tab:hover:!selected {
                background-color: #3d566e;
            }
        """)
        
        # Crear pestañas
        self.accounts_tab = self._create_accounts_tab()
        self.mount_tab = self._create_mount_tab()
        self.files_tab = self._create_files_tab()
        
        self.tabs.addTab(self.accounts_tab, "👤 Cuentas")
        self.tabs.addTab(self.mount_tab, "💿 Montar")
        self.tabs.addTab(self.files_tab, "📁 Archivos")
        
        layout.addWidget(self.tabs, 1)
        
        # Barra de estado
        self.status_bar = QLabel("Listo")
        self.status_bar.setStyleSheet("""
            background-color: #1a1a2e;
            color: #7f8c8d;
            padding: 8px 15px;
            border-radius: 5px;
        """)
        layout.addWidget(self.status_bar)
    
    def _create_accounts_tab(self) -> QWidget:
        """Crea la pestaña de gestión de cuentas"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        
        # Selector de cuenta existente
        account_group = QGroupBox("Cuenta Activa")
        account_layout = QHBoxLayout()
        
        self.account_selector = QComboBox()
        self.account_selector.setMinimumHeight(35)
        self.account_selector.currentIndexChanged.connect(self._on_account_changed)
        account_layout.addWidget(self.account_selector, 1)
        
        self.validate_btn = QPushButton("✓ Validar")
        self.validate_btn.clicked.connect(self._validate_current_account)
        account_layout.addWidget(self.validate_btn)
        
        self.remove_account_btn = QPushButton("🗑️ Eliminar")
        self.remove_account_btn.setStyleSheet("background-color: #e74c3c;")
        self.remove_account_btn.clicked.connect(self._remove_current_account)
        account_layout.addWidget(self.remove_account_btn)
        
        account_group.setLayout(account_layout)
        layout.addWidget(account_group)
        
        # Formulario para agregar cuenta (dinámico)
        self.add_account_group = QGroupBox("Agregar Nueva Cuenta")
        self.add_account_layout = QFormLayout()
        self.add_account_fields = {}
        self.add_account_group.setLayout(self.add_account_layout)
        layout.addWidget(self.add_account_group)
        
        # Botón de agregar
        self.add_account_btn = QPushButton("➕ Agregar Cuenta")
        self.add_account_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                font-weight: bold;
                padding: 12px;
                border-radius: 5px;
            }
            QPushButton:hover { background-color: #219a52; }
        """)
        self.add_account_btn.clicked.connect(self._add_account)
        layout.addWidget(self.add_account_btn)
        
        layout.addStretch()
        return tab
    
    def _create_mount_tab(self) -> QWidget:
        """Crea la pestaña de montaje"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        
        # Información de montaje actual
        status_group = QGroupBox("Estado de Montaje")
        status_layout = QVBoxLayout()
        
        self.mount_status = QLabel("⭕ Sin montar")
        self.mount_status.setFont(QFont("Segoe UI", 12))
        status_layout.addWidget(self.mount_status)
        
        status_group.setLayout(status_layout)
        layout.addWidget(status_group)
        
        # Configuración de montaje
        config_group = QGroupBox("Configuración")
        config_layout = QFormLayout()
        
        # Selector de bucket/carpeta (solo visible para S3)
        self.bucket_selector = QComboBox()
        self.bucket_selector.setMinimumHeight(35)
        self.bucket_label = QLabel("Bucket:")
        config_layout.addRow(self.bucket_label, self.bucket_selector)
        
        # Selector de letra de unidad
        self.drive_selector = QComboBox()
        self.drive_selector.addItems([chr(i) for i in range(ord('V'), ord('Z')+1)])
        self.drive_selector.setMinimumHeight(35)
        config_layout.addRow("Letra de Unidad:", self.drive_selector)
        
        config_group.setLayout(config_layout)
        layout.addWidget(config_group)
        
        # Botones de acción
        actions_layout = QHBoxLayout()
        
        self.mount_btn = QPushButton("🔗 Montar como Unidad")
        self.mount_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                font-weight: bold;
                padding: 15px;
                border-radius: 5px;
                font-size: 13px;
            }
            QPushButton:hover { background-color: #219a52; }
        """)
        self.mount_btn.clicked.connect(self._mount_drive)
        
        self.unmount_btn = QPushButton("🔌 Desmontar")
        self.unmount_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                font-weight: bold;
                padding: 15px;
                border-radius: 5px;
                font-size: 13px;
            }
            QPushButton:hover { background-color: #c0392b; }
        """)
        self.unmount_btn.clicked.connect(self._unmount_drive)
        
        self.open_drive_btn = QPushButton("📂 Abrir en Explorador")
        self.open_drive_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                font-weight: bold;
                padding: 15px;
                border-radius: 5px;
                font-size: 13px;
            }
            QPushButton:hover { background-color: #2980b9; }
        """)
        self.open_drive_btn.clicked.connect(self._open_drive)
        
        actions_layout.addWidget(self.mount_btn)
        actions_layout.addWidget(self.unmount_btn)
        actions_layout.addWidget(self.open_drive_btn)
        
        layout.addLayout(actions_layout)
        layout.addStretch()
        
        return tab
    
    def _create_files_tab(self) -> QWidget:
        """Crea la pestaña de archivos"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        
        # Acciones rápidas
        actions_group = QGroupBox("Acciones Rápidas")
        actions_layout = QHBoxLayout()
        
        self.upload_file_btn = QPushButton("📤 Subir Archivo")
        self.upload_file_btn.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6;
                color: white;
                font-weight: bold;
                padding: 12px 20px;
                border-radius: 5px;
            }
            QPushButton:hover { background-color: #8e44ad; }
        """)
        self.upload_file_btn.clicked.connect(self._upload_file)
        
        self.upload_folder_btn = QPushButton("📁 Respaldar Carpeta")
        self.upload_folder_btn.setStyleSheet("""
            QPushButton {
                background-color: #e67e22;
                color: white;
                font-weight: bold;
                padding: 12px 20px;
                border-radius: 5px;
            }
            QPushButton:hover { background-color: #d35400; }
        """)
        self.upload_folder_btn.clicked.connect(self._upload_folder)
        
        actions_layout.addWidget(self.upload_file_btn)
        actions_layout.addWidget(self.upload_folder_btn)
        actions_group.setLayout(actions_layout)
        layout.addWidget(actions_group)
        
        # Explorador de archivos (simplificado)
        browser_group = QGroupBox("Contenido del Almacenamiento")
        browser_layout = QVBoxLayout()
        
        self.path_label = QLabel("📍 /")
        self.path_label.setStyleSheet("color: #3498db; font-weight: bold;")
        browser_layout.addWidget(self.path_label)
        
        self.files_list = QListWidget()
        self.files_list.setMinimumHeight(200)
        browser_layout.addWidget(self.files_list)
        
        refresh_btn = QPushButton("🔄 Actualizar")
        refresh_btn.clicked.connect(self._refresh_files)
        browser_layout.addWidget(refresh_btn)
        
        browser_group.setLayout(browser_layout)
        layout.addWidget(browser_group)
        
        # Barra de progreso
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        return tab
    
    def set_storage_type(self, storage_id: str, storage_handler):
        """
        Configura el panel para un tipo de almacenamiento específico.
        
        Args:
            storage_id: ID del tipo de almacenamiento
            storage_handler: Instancia de BaseStorage
        """
        self._current_storage = storage_id
        self.storage_handlers[storage_id] = storage_handler
        
        # Actualizar header
        info = storage_handler.get_display_info()
        self.storage_icon.setText(info['icon'])
        self.storage_title.setText(info['name'])
        self.storage_desc.setText(info['description'])
        self.storage_title.setStyleSheet(f"color: {info['color']};")
        
        # Actualizar formulario de agregar cuenta
        self._setup_account_form(storage_handler)
        
        # Mostrar/ocultar selector de bucket según tipo
        has_buckets = storage_handler.supports_buckets()
        self.bucket_label.setVisible(has_buckets)
        self.bucket_selector.setVisible(has_buckets)
        
        # Recargar cuentas
        self._refresh_accounts()
        
        self.status_bar.setText(f"Tipo de almacenamiento: {info['name']}")
    
    def _setup_account_form(self, storage_handler):
        """Configura el formulario de agregar cuenta según el tipo"""
        # Limpiar campos anteriores
        while self.add_account_layout.count():
            item = self.add_account_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.add_account_fields.clear()
        
        # Crear campos según el tipo
        for field in storage_handler.get_account_form_fields():
            if field['type'] == 'text':
                widget = QLineEdit()
                widget.setPlaceholderText(field.get('placeholder', ''))
            elif field['type'] == 'password':
                widget = QLineEdit()
                widget.setEchoMode(QLineEdit.EchoMode.Password)
                widget.setPlaceholderText(field.get('placeholder', ''))
            elif field['type'] == 'select':
                widget = QComboBox()
                for opt in field.get('options', []):
                    widget.addItem(opt['label'], opt['value'])
            else:
                widget = QLineEdit()
            
            widget.setMinimumHeight(35)
            self.add_account_fields[field['name']] = widget
            self.add_account_layout.addRow(field['label'] + ":", widget)
    
    def _refresh_accounts(self):
        """Actualiza la lista de cuentas del tipo actual"""
        if not self._current_storage or self._current_storage not in self.storage_handlers:
            return
        
        handler = self.storage_handlers[self._current_storage]
        accounts = handler.get_accounts()
        
        self.account_selector.clear()
        for acc in accounts:
            self.account_selector.addItem(f"{acc.name}", acc.id)
        
        if accounts:
            self._current_account = accounts[0]
            self._load_account_data()
    
    def _on_account_changed(self, index):
        """Manejador de cambio de cuenta"""
        if index < 0 or not self._current_storage:
            return
        
        handler = self.storage_handlers[self._current_storage]
        accounts = handler.get_accounts()
        
        if index < len(accounts):
            self._current_account = accounts[index]
            self._load_account_data()
    
    def _load_account_data(self):
        """Carga datos específicos de la cuenta actual"""
        if not self._current_account or not self._current_storage:
            return
        
        handler = self.storage_handlers[self._current_storage]
        
        # Si soporta buckets, cargar lista
        if handler.supports_buckets():
            try:
                buckets, error = handler.get_buckets(self._current_account)
                self.bucket_selector.clear()
                if buckets:
                    self.bucket_selector.addItems(buckets)
            except Exception as e:
                self.status_bar.setText(f"Error cargando buckets: {e}")
    
    def _add_account(self):
        """Agrega una nueva cuenta"""
        if not self._current_storage:
            return
        
        handler = self.storage_handlers[self._current_storage]
        
        # Recoger valores del formulario
        kwargs = {}
        for field in handler.get_account_form_fields():
            widget = self.add_account_fields.get(field['name'])
            if widget:
                if isinstance(widget, QComboBox):
                    kwargs[field['name']] = widget.currentData()
                else:
                    kwargs[field['name']] = widget.text().strip()
        
        # Validar campos requeridos
        for field in handler.get_account_form_fields():
            if field.get('required') and not kwargs.get(field['name']):
                QMessageBox.warning(self, "Campo requerido", 
                                   f"El campo '{field['label']}' es obligatorio.")
                return
        
        # Agregar cuenta
        success, message = handler.add_account(**kwargs)
        
        if success:
            QMessageBox.information(self, "Éxito", message)
            # Limpiar formulario
            for widget in self.add_account_fields.values():
                if isinstance(widget, QLineEdit):
                    widget.clear()
            self._refresh_accounts()
        else:
            QMessageBox.critical(self, "Error", message)
    
    def _validate_current_account(self):
        """Valida la cuenta actual"""
        if not self._current_account or not self._current_storage:
            return
        
        handler = self.storage_handlers[self._current_storage]
        success, message = handler.validate_account(self._current_account)
        
        if success:
            QMessageBox.information(self, "Cuenta Válida ✅", message)
        else:
            QMessageBox.warning(self, "Error de Validación", message)
    
    def _remove_current_account(self):
        """Elimina la cuenta actual"""
        if not self._current_account or not self._current_storage:
            return
        
        reply = QMessageBox.question(
            self, "Confirmar Eliminación",
            f"¿Eliminar la cuenta '{self._current_account.name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            handler = self.storage_handlers[self._current_storage]
            success, message = handler.remove_account(self._current_account.id)
            
            if success:
                self._refresh_accounts()
                self.status_bar.setText(message)
            else:
                QMessageBox.critical(self, "Error", message)
    
    def _mount_drive(self):
        """Monta la unidad"""
        if not self._current_account or not self._current_storage:
            QMessageBox.warning(self, "Error", "Selecciona una cuenta primero")
            return
        
        handler = self.storage_handlers[self._current_storage]
        drive_letter = self.drive_selector.currentText()
        
        options = {}
        if handler.supports_buckets():
            bucket = self.bucket_selector.currentText()
            if not bucket:
                QMessageBox.warning(self, "Error", "Selecciona un bucket")
                return
            options['bucket_name'] = bucket
        
        self.status_bar.setText(f"Montando {drive_letter}:...")
        
        success, message, _ = handler.mount(
            self._current_account, 
            drive_letter,
            **options
        )
        
        if success:
            self.mount_status.setText(f"✅ Montado en {drive_letter}:")
            self.status_bar.setText(message)
            QMessageBox.information(self, "Éxito", message)
        else:
            self.mount_status.setText("❌ Error de montaje")
            self.status_bar.setText(f"Error: {message}")
            QMessageBox.critical(self, "Error de Montaje", message)
    
    def _unmount_drive(self):
        """Desmonta la unidad"""
        if not self._current_storage:
            return
        
        handler = self.storage_handlers[self._current_storage]
        drive_letter = self.drive_selector.currentText()
        
        success, message = handler.unmount(drive_letter)
        
        if success:
            self.mount_status.setText("⭕ Sin montar")
            self.status_bar.setText(message)
        else:
            QMessageBox.warning(self, "Error", message)
    
    def _open_drive(self):
        """Abre la unidad en el explorador"""
        import subprocess
        drive_letter = self.drive_selector.currentText()
        subprocess.Popen(f'explorer {drive_letter}:')
    
    def _upload_file(self):
        """Sube un archivo"""
        if not self._current_account or not self._current_storage:
            QMessageBox.warning(self, "Error", "Selecciona una cuenta primero")
            return
        
        file_path, _ = QFileDialog.getOpenFileName(self, "Seleccionar Archivo")
        if not file_path:
            return
        
        handler = self.storage_handlers[self._current_storage]
        
        # Determinar destino
        if handler.supports_buckets():
            bucket = self.bucket_selector.currentText()
            if not bucket:
                QMessageBox.warning(self, "Error", "Selecciona un bucket")
                return
            remote_path = bucket
        else:
            remote_path = "/"
        
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(50)
        self.status_bar.setText(f"Subiendo archivo...")
        
        success, message = handler.upload_file(self._current_account, file_path, remote_path)
        
        self.progress_bar.setVisible(False)
        
        if success:
            self.status_bar.setText("Archivo subido correctamente")
            QMessageBox.information(self, "Éxito", message)
        else:
            self.status_bar.setText(f"Error: {message}")
            QMessageBox.critical(self, "Error", message)
    
    def _upload_folder(self):
        """Sube una carpeta"""
        if not self._current_account or not self._current_storage:
            QMessageBox.warning(self, "Error", "Selecciona una cuenta primero")
            return
        
        folder_path = QFileDialog.getExistingDirectory(self, "Seleccionar Carpeta")
        if not folder_path:
            return
        
        handler = self.storage_handlers[self._current_storage]
        
        if handler.supports_buckets():
            bucket = self.bucket_selector.currentText()
            if not bucket:
                QMessageBox.warning(self, "Error", "Selecciona un bucket")
                return
            remote_path = bucket
        else:
            remote_path = "/"
        
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(50)
        self.status_bar.setText(f"Respaldando carpeta...")
        
        success, message = handler.upload_folder(self._current_account, folder_path, remote_path)
        
        self.progress_bar.setVisible(False)
        
        if success:
            self.status_bar.setText("Carpeta respaldada correctamente")
            QMessageBox.information(self, "Éxito", message)
        else:
            self.status_bar.setText(f"Error: {message}")
            QMessageBox.critical(self, "Error", message)
    
    def _refresh_files(self):
        """Actualiza la lista de archivos"""
        if not self._current_account or not self._current_storage:
            return
        
        handler = self.storage_handlers[self._current_storage]
        items, error = handler.list_contents(self._current_account, "/")
        
        self.files_list.clear()
        
        if error:
            self.files_list.addItem(f"❌ Error: {error}")
            return
        
        for item in items:
            icon = "📁" if item.is_dir else "📄"
            size_str = f" ({item.size} bytes)" if not item.is_dir else ""
            list_item = QListWidgetItem(f"{icon} {item.name}{size_str}")
            self.files_list.addItem(list_item)
        
        if not items:
            self.files_list.addItem("(vacío)")
