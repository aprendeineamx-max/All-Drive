from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QFormLayout, 
                             QHBoxLayout, QListWidget, QMessageBox, QCheckBox, QGroupBox, QTabWidget)
from PyQt6.QtCore import pyqtSignal, Qt

class SettingsWindow(QWidget):
    profiles_updated = pyqtSignal()

    def __init__(self, config_manager, main_window=None):
        super().__init__()
        self.config_manager = config_manager
        self.main_window = main_window
        self.translations = getattr(main_window, "translations", None)
        self.setWindowTitle(self.tr("settings_window_title"))
        self.setGeometry(150, 150, 600, 500)

        # ===== PESTAÑAS =====
        self.tabs = QTabWidget()
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.addWidget(self.tabs)
        
        # Pestaña 1: Perfiles
        profiles_tab = QWidget()
        profiles_layout = QHBoxLayout(profiles_tab)
        profiles_layout.setContentsMargins(10, 10, 10, 10)
        profiles_layout.setSpacing(20)

        # Left side: List of profiles
        left_layout = QVBoxLayout()
        left_label = QLabel(self.tr("settings_existing_profiles"))
        left_label.setStyleSheet("font-weight: bold; font-size: 11pt; color: #2c3e50;")
        left_layout.addWidget(left_label)
        
        self.profile_list = QListWidget()
        self.profile_list.itemClicked.connect(self.on_profile_selected)
        self.profile_list.setStyleSheet("""
            QListWidget {
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                padding: 5px;
            }
            QListWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
        """)
        left_layout.addWidget(self.profile_list)
        
        # ===== NUEVO: Botones de gestión de perfiles =====
        buttons_layout = QVBoxLayout()
        buttons_layout.setSpacing(10)
        
        self.new_profile_btn = QPushButton("➕ Nuevo Perfil")
        self.new_profile_btn.clicked.connect(self.create_new_profile)
        self.new_profile_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                font-weight: bold;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover { background-color: #229954; }
        """)
        
        self.edit_profile_btn = QPushButton("✏️ Editar Perfil")
        self.edit_profile_btn.clicked.connect(self.edit_selected_profile)
        self.edit_profile_btn.setEnabled(False)
        self.edit_profile_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                font-weight: bold;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover { background-color: #2980b9; }
            QPushButton:disabled { background-color: #95a5a6; }
        """)
        
        self.delete_button = QPushButton("🗑️ Eliminar Perfil")
        self.delete_button.clicked.connect(self.delete_profile)
        self.delete_button.setEnabled(False)
        self.delete_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                font-weight: bold;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover { background-color: #c0392b; }
            QPushButton:disabled { background-color: #95a5a6; }
        """)
        
        buttons_layout.addWidget(self.new_profile_btn)
        buttons_layout.addWidget(self.edit_profile_btn)
        buttons_layout.addWidget(self.delete_button)
        buttons_layout.addStretch()
        
        left_layout.addLayout(buttons_layout)

        # Right side: Info panel
        right_layout = QVBoxLayout()
        right_label = QLabel("📋 Información del Perfil")
        right_label.setStyleSheet("font-weight: bold; font-size: 11pt; color: #2c3e50;")
        right_layout.addWidget(right_label)
        
        self.profile_info_label = QLabel(
            "Selecciona un perfil de la lista para ver sus detalles.\n\n"
            "💡 Usa los botones de la izquierda para:\n"
            "• Crear un nuevo perfil\n"
            "• Editar el perfil seleccionado\n"
            "• Eliminar el perfil seleccionado"
        )
        self.profile_info_label.setWordWrap(True)
        self.profile_info_label.setStyleSheet("""
            QLabel {
                background-color: #ecf0f1;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                padding: 20px;
                color: #34495e;
            }
        """)
        self.profile_info_label.setMinimumHeight(200)
        right_layout.addWidget(self.profile_info_label)
        right_layout.addStretch()

        profiles_layout.addLayout(left_layout, 1)
        profiles_layout.addLayout(right_layout, 2)
        
        self.tabs.addTab(profiles_tab, self.tr("settings_profiles_tab"))
        
        # Pestaña 2: Configuración General
        general_tab = QWidget()
        general_layout = QVBoxLayout(general_tab)
        general_layout.setContentsMargins(20, 20, 20, 20)
        general_layout.setSpacing(15)
        
        # Grupo: Inicio Automático
        startup_group = QGroupBox(self.tr("settings_startup_group"))
        startup_layout = QVBoxLayout()
        
        self.chk_startup = QCheckBox(self.tr("settings_startup_checkbox"))
        if self.main_window and hasattr(self.main_window, 'startup_manager'):
            self.chk_startup.setChecked(self.main_window.startup_manager.is_enabled())
        self.chk_startup.stateChanged.connect(self.on_startup_changed)
        startup_layout.addWidget(self.chk_startup)
        
        self.chk_minimized = QCheckBox(self.tr("settings_startup_minimized"))
        if self.main_window and hasattr(self.main_window, 'startup_manager'):
            self.chk_minimized.setEnabled(self.chk_startup.isChecked())
        self.chk_minimized.stateChanged.connect(self.on_startup_minimized_changed)
        startup_layout.addWidget(self.chk_minimized)
        
        startup_info = QLabel(self.tr("settings_startup_info"))
        startup_info.setWordWrap(True)
        startup_info.setStyleSheet("color: #888; font-size: 9pt; margin-top: 10px;")
        startup_layout.addWidget(startup_info)
        
        startup_group.setLayout(startup_layout)
        general_layout.addWidget(startup_group)
        
        # Grupo: Notificaciones
        notifications_group = QGroupBox(self.tr("settings_notifications_group"))
        notifications_layout = QVBoxLayout()
        
        self.chk_notifications = QCheckBox(self.tr("settings_notifications_checkbox"))
        if self.main_window and hasattr(self.main_window, 'notification_manager'):
            self.chk_notifications.setChecked(self.main_window.notification_manager.enabled)
        else:
            self.chk_notifications.setChecked(True)
        self.chk_notifications.stateChanged.connect(self.on_notifications_changed)
        notifications_layout.addWidget(self.chk_notifications)
        
        notifications_info = QLabel(self.tr("settings_notifications_info"))
        notifications_info.setWordWrap(True)
        notifications_info.setStyleSheet("color: #888; font-size: 9pt; margin-top: 10px;")
        notifications_layout.addWidget(notifications_info)
        
        notifications_group.setLayout(notifications_layout)
        general_layout.addWidget(notifications_group)
        
        general_layout.addStretch()
        
        self.tabs.addTab(general_tab, self.tr("settings_general_tab"))

        self.refresh_profile_list()

    def refresh_profile_list(self):
        """Actualizar lista de perfiles"""
        self.profile_list.clear()
        self.profile_list.addItems(self.config_manager.list_profiles())
    
    def on_profile_selected(self, item):
        """Mostrar información del perfil seleccionado"""
        profile_name = item.text()
        config = self.config_manager.get_profile_data(profile_name)
        
        if config:
            # Mostrar información del perfil (sin mostrar credenciales completas)
            access_key_preview = config.get('access_key', '')[:10] + "..." if config.get('access_key') else "N/A"
            host_base = config.get('host_base', 'N/A')
            
            info_text = (
                f"📝 Perfil: {profile_name}\n\n"
                f"🔑 Access Key: {access_key_preview}\n"
                f"🌐 Endpoint: {host_base}\n\n"
                f"💡 Usa 'Editar Perfil' para modificar las credenciales"
            )
            self.profile_info_label.setText(info_text)
        
        # Habilitar botones de editar/eliminar
        self.edit_profile_btn.setEnabled(True)
        self.delete_button.setEnabled(True)
    
    def create_new_profile(self):
        """Crear nuevo perfil mediante diálogo"""
        try:
            from ui.profile_dialog import ProfileDialog
        except ImportError as e:
            QMessageBox.critical(self, "Error", f"No se pudo cargar el diálogo: {e}")
            return
        
        dialog = ProfileDialog(self, profile_data=None, translations=self.translations)
        
        if dialog.exec() != dialog.DialogCode.Accepted:
            return
        
        profile_data = dialog.get_profile_data()
        
        try:
            success, message = self.config_manager.create_profile(
                profile_data['name'],
                profile_data['access_key'],
                profile_data['secret_key'],
                profile_data['host_base']
            )
            
            QMessageBox.information(self, "✅ Éxito", message)
            self.profiles_updated.emit()
            self.refresh_profile_list()
            
        except ValueError as e:
            QMessageBox.critical(self, "❌ Error", str(e))
        except Exception as e:
            QMessageBox.critical(self, "❌ Error", f"Error inesperado: {str(e)}")
    
    def edit_selected_profile(self):
        """Editar perfil seleccionado"""
        selected_items = self.profile_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Advertencia", "Selecciona un perfil primero")
            return
        
        profile_name = selected_items[0].text()
        config = self.config_manager.get_profile_data(profile_name)
        
        if not config:
            QMessageBox.warning(self, "Error", "No se pudo cargar el perfil")
            return
        
        try:
            from ui.profile_dialog import ProfileDialog
        except ImportError as e:
            QMessageBox.critical(self, "Error", f"No se pudo cargar el diálogo: {e}")
            return
        
        # Preparar datos para el diálogo (incluir nombre)
        profile_data_for_dialog = {
            'name': profile_name,
            'access_key': config.get('access_key', ''),
            'secret_key': config.get('secret_key', ''),
            'host_base': config.get('host_base', '')
        }
        
        dialog = ProfileDialog(self, profile_data=profile_data_for_dialog, translations=self.translations)
        
        if dialog.exec() != dialog.DialogCode.Accepted:
            return
        
        new_data = dialog.get_profile_data()
        
        # Solo actualizar campos que cambiaron
        update_fields = {}
        if new_data['access_key'] != config.get('access_key'):
            update_fields['access_key'] = new_data['access_key']
        if new_data['secret_key'] != config.get('secret_key'):
            update_fields['secret_key'] = new_data['secret_key']
        if new_data['host_base'] != config.get('host_base'):
            update_fields['host_base'] = new_data['host_base']
        
        if not update_fields:
            QMessageBox.information(self, "Info", "No se realizaron cambios")
            return
        
        try:
            success, message = self.config_manager.update_profile(profile_name, update_fields)
            
            QMessageBox.information(self, "✅ Éxito", message)
            self.profiles_updated.emit()
            self.refresh_profile_list()
            
            # Actualizar panel de información
            self.on_profile_selected(self.profile_list.currentItem())
            
        except ValueError as e:
            QMessageBox.critical(self, "❌ Error", str(e))
        except Exception as e:
            QMessageBox.critical(self, "❌ Error", f"Error inesperado: {str(e)}")

    def delete_profile(self):
        """Eliminar perfil seleccionado con confirmación"""
        selected_items = self.profile_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, self.tr("warning"), "Selecciona un perfil primero")
            return

        profile_name = selected_items[0].text()
        
        # Prevenir eliminación del perfil activo
        if self.main_window and hasattr(self.main_window, 'profile_selector'):
            active_profile = self.main_window.profile_selector.currentText()
            if profile_name == active_profile:
                QMessageBox.warning(
                    self,
                    "⚠️ Advertencia",
                    f"No puedes eliminar el perfil activo '{profile_name}'.\n\n"
                    f"Primero cambia a otro perfil en la ventana principal."
                )
                return
        
        reply = QMessageBox.question(
            self,
            "⚠️ Confirmar Eliminación",
            f"¿Estás seguro de que deseas eliminar el perfil '{profile_name}'?\n\n"
            f"Esta acción no se puede deshacer.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                success, message = self.config_manager.delete_profile(profile_name)
                
                QMessageBox.information(self, "✅ Éxito", message)
                self.profiles_updated.emit()
                self.refresh_profile_list()
                
                # Limpiar panel de información
                self.profile_info_label.setText(
                    "Selecciona un perfil de la lista para ver sus detalles."
                )
                self.edit_profile_btn.setEnabled(False)
                self.delete_button.setEnabled(False)
                
            except ValueError as e:
                QMessageBox.critical(self, "❌ Error", str(e))
            except Exception as e:
                QMessageBox.critical(self, "❌ Error", f"Error inesperado: {str(e)}")

    
    def on_startup_changed(self, state):
        """Callback cuando cambia el checkbox de inicio automático"""
        if not self.main_window or not hasattr(self.main_window, 'startup_manager'):
            return
        
        enabled = state == Qt.CheckState.Checked
        minimized = self.chk_minimized.isChecked()
        
        success, message = self.main_window.startup_manager.toggle(enabled, minimized)
        
        if success:
            if self.main_window.notification_manager:
                self.main_window.notification_manager.success(
                    self.tr("settings_notification_saved_title"),
                    message
                )
        else:
            if self.main_window.notification_manager:
                self.main_window.notification_manager.error(
                    self.tr("settings_notification_error_title"),
                    message
                )
        
        self.chk_minimized.setEnabled(enabled)
    
    def on_startup_minimized_changed(self, state):
        """Callback cuando cambia el checkbox de iniciar minimizado"""
        if not self.main_window or not hasattr(self.main_window, 'startup_manager'):
            return
        
        if not self.chk_startup.isChecked():
            return
        
        minimized = state == Qt.CheckState.Checked
        success, message = self.main_window.startup_manager.enable(minimized)
        
        if success and self.main_window.notification_manager:
            self.main_window.notification_manager.info(
                self.tr("settings_notification_updated_title"),
                message
            )
    
    def on_notifications_changed(self, state):
        """Callback cuando cambia el checkbox de notificaciones"""
        if not self.main_window or not hasattr(self.main_window, 'notification_manager'):
            return
        
        enabled = state == Qt.CheckState.Checked
        self.main_window.notification_manager.set_enabled(enabled)

    def tr(self, key):
        if self.translations:
            return self.translations.get(key)
        return key
