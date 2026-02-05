from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QComboBox, 
    QLabel, QFileDialog, QStatusBar, QHBoxLayout, QGroupBox, 
    QMessageBox, QLineEdit, QTabWidget, QTextEdit, QProgressBar,
    QMenu, QScrollArea, QSizePolicy, QToolButton, QSystemTrayIcon,
    QStyle, QDialog, QStackedWidget
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QAction
from config_manager import ConfigManager
from s3_handler import S3Handler
from ui.settings_window import SettingsWindow
from rclone_manager import RcloneManager
from file_watcher import RealTimeSync
from drive_detector import DriveDetector
from startup_manager import StartupManager
from notification_manager import NotificationManager, NotificationType
from core.task_runner import TaskRunner
from multiple_mount_manager import MultipleMountManager
from ui.multi_mounts_widget import MultiMountsWidget
from ui.tools_tab import ToolsTab
from ui.plan_editor import PlanEditorDialog
from ui.recovery_tab import RecoveryTab
from ui.monitoring_tab import MonitoringTab

# ... (omitting intermediate lines)
from ui.mega_tab import MegaTab
from ui.azure_tab import AzureTab
from ui.gcp_tab import GCPTab
from ui.sidebar import Sidebar


# ===== MEJORA Task5: Auditoría y Monitor =====
try:
    from core.audit_logger import get_audit_logger, AuditEventType
    AUDIT_AVAILABLE = True
except ImportError:
    AUDIT_AVAILABLE = False
    AuditEventType = None

try:
    from core.state_monitor import get_state_monitor, ComponentStatus
    STATE_MONITOR_AVAILABLE = True
except ImportError:
    STATE_MONITOR_AVAILABLE = False
    ComponentStatus = None

try:
    from core.task_scheduler import TaskScheduler
    SCHEDULER_AVAILABLE = True
except ImportError:
    SCHEDULER_AVAILABLE = False
    TaskScheduler = None

# ===== MEJORA #48: Manejo de Errores Mejorado =====
try:
    from error_handler import handle_error, get_error_handler
    ERROR_HANDLING_AVAILABLE = True
except ImportError:
    ERROR_HANDLING_AVAILABLE = False

# ===== MEJORA #47: Sistema de Logging =====
try:
    from logger_manager import get_logger
    logger = get_logger(__name__)
    LOGGING_AVAILABLE = True
except ImportError:
    LOGGING_AVAILABLE = False
    logger = None

import os

class UploadThread(QThread):
    finished = pyqtSignal(bool, dict)

    def __init__(self, s3_handler, bucket_name, file_path):
        super().__init__()
        self.s3_handler = s3_handler
        self.bucket_name = bucket_name
        self.file_path = file_path

    def run(self):
        try:
            success = self.s3_handler.upload_file(self.bucket_name, self.file_path)
            file_name = os.path.basename(self.file_path)
            if success:
                self.finished.emit(True, {"file": file_name})
            else:
                error_message = getattr(self.s3_handler, "last_error", "") or ""
                self.finished.emit(False, {"file": file_name, "error": error_message})
        except Exception as e:
            self.finished.emit(False, {"file": os.path.basename(self.file_path), "error": str(e)})


class BackupThread(QThread):
    progress = pyqtSignal(int, dict)
    finished = pyqtSignal(bool, dict)

    def __init__(self, s3_handler, bucket_name, folder_path):
        super().__init__()
        self.s3_handler = s3_handler
        self.bucket_name = bucket_name
        self.folder_path = folder_path

    def run(self):
        try:
            files = []
            for root, dirs, filenames in os.walk(self.folder_path):
                for filename in filenames:
                    files.append(os.path.join(root, filename))
            
            total = len(files)
            if total == 0:
                self.finished.emit(False, {"reason": "no_files"})
                return

            for index, file_path in enumerate(files, start=1):
                relative_path = os.path.relpath(file_path, self.folder_path)
                self.progress.emit(
                    int(((index - 1) * 100) / total),
                    {
                        "current": index,
                        "total": total,
                        "file": relative_path,
                    },
                )
                self.s3_handler.upload_file(self.bucket_name, file_path, relative_path)
            
            self.finished.emit(True, {"total": total})
        except Exception as e:
            self.finished.emit(False, {"reason": "exception", "detail": str(e)})


class MainWindow(QMainWindow):
    def __init__(self, theme_manager=None, translations=None, save_preferences_callback=None):
        super().__init__()

        # Store references to theme manager and translations
        self.theme_manager = theme_manager
        self.translations = translations
        self.save_preferences_callback = save_preferences_callback
        
        # Initialize UI
        self.setWindowTitle(self.tr("window_title"))
        self.setGeometry(100, 100, 900, 700)  # Ventana más grande y responsiva
        self.setMinimumSize(800, 600)  # Tamaño mínimo para evitar problemas de visualización

        self.config_manager = ConfigManager()
        self.s3_handler = None
        self.rclone_manager = RcloneManager(self.config_manager)
        self.multiple_mount_manager = None
        self.real_time_sync = None
        self.upload_thread = None
        self.backup_thread = None
        self.install_winfsp_callback = None
        self.tray_icon = None
        self._tray_menu = None
        self._tray_actions = {}
        self._is_in_tray = False
        self._force_quit = False
        self._tray_notified = False
        self._close_without_unmount = False  # Flag para cerrar sin desmontar
        self.task_runner = TaskRunner(self)
        self._refreshing_buckets = False
        self._current_bucket_handler = None
        
        # ===== QUICK WINS: Inicializar gestores =====
        # Gestor de inicio automático
        self.startup_manager = StartupManager()
        
        # Gestor de notificaciones (se inicializará después del tray_icon)
        self.notification_manager = None
        
        # ===== Task5: Inicializar Auditoría, Monitor y Scheduler =====
        if AUDIT_AVAILABLE:
            self.audit_logger = get_audit_logger()
        else:
            self.audit_logger = None

        # ===== SETUP UI CORE =====
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # ===== NEW: Layout con barra lateral =====
        self.root_layout = QHBoxLayout(self.central_widget)
        self.root_layout.setContentsMargins(0, 0, 0, 0)
        self.root_layout.setSpacing(0)
        
        # Sidebar izquierda
        self._setup_sidebar()
        
        # Contenedor derecho para el contenido original
        self.content_container = QWidget()
        self.main_layout = QVBoxLayout(self.content_container)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.root_layout.addWidget(self.content_container, 1)

        self.setup_top_controls()



        # ===== STACK PRINCIPAL (Para cambiar entre Vultr, MEGA, Azure) =====
        self.main_stack = QStackedWidget()
        self.main_layout.addWidget(self.main_stack)

        # 1. Contenedor Vultr (QTabWidget original)
        self.vultr_container = QWidget()
        vultr_layout = QVBoxLayout(self.vultr_container)
        vultr_layout.setContentsMargins(0, 0, 0, 0)
        
        self.vultr_tabs = QTabWidget()
        vultr_layout.addWidget(self.vultr_tabs)
        
        self.main_stack.addWidget(self.vultr_container) # Index 0

        # 2. Inicializar Widgets de Vultr
        self.main_tab = QWidget()
        self.mount_tab = QWidget()
        self.sync_tab = QWidget()
        self.advanced_tab = QWidget()
        self.monitoring_tab = MonitoringTab()

        # 3. Setup Main Tab (creates profile_selector and bucket_selector)
        self.setup_main_tab()

        # 4. Initialize Dependent Tabs
        self.recovery_tab = RecoveryTab(self.rclone_manager)
        self.tools_tab = ToolsTab(self.rclone_manager, self.config_manager)

        # 5. Add Tabs to Vultr Widget
        self.vultr_tabs.addTab(self.main_tab, "🏠 " + self.tr("tab_main"))
        self.vultr_tabs.addTab(self.mount_tab, "💿 " + self.tr("tab_mount"))
        self.vultr_tabs.addTab(self.sync_tab, "🔄 " + self.tr("tab_sync"))
        self.vultr_tabs.addTab(self.recovery_tab, "🚑 " + self.tr("tab_recovery"))
        self.vultr_tabs.addTab(self.tools_tab, "🛠️ " + self.tr("tab_tools"))
        self.vultr_tabs.addTab(self.monitoring_tab, "📊 " + self.tr("tab_monitor"))
        self.vultr_tabs.addTab(self.advanced_tab, "⚙️ " + self.tr("tab_advanced"))
        
        # 6. MEGA Tab (Container propio)
        self.mega_tab = MegaTab(self.rclone_manager, self)
        self.main_stack.addWidget(self.mega_tab) # Index 1
        
        # 7. Azure Tab (Container propio)
        self.azure_tab = AzureTab(self)
        self.main_stack.addWidget(self.azure_tab) # Index 2
        
        # 8. GCP Tab (Container propio)
        self.gcp_tab = GCPTab(self)
        self.main_stack.addWidget(self.gcp_tab) # Index 3

        # 5. Setup Remaining Tabs Content
        self.setup_mount_tab()
        self.setup_sync_tab()
        self.setup_advanced_tab()
        
        # Connect Global Logging Signal
        if LOGGING_AVAILABLE:
            from logger_manager import get_logger_manager
            # Use singleton accessor
            get_logger_manager().log_received.connect(self.monitoring_tab.add_log_entry)

        # Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.main_layout.addWidget(self.progress_bar)

        # ===== MEJORA: Cargar perfil automáticamente al iniciar =====
        # Cargar el primer perfil disponible automáticamente
        if self.profile_selector.count() > 0:
            # Cargar perfil después de que la ventana se muestre (no bloquear inicio)
            QTimer.singleShot(500, lambda: self._auto_load_profile())
        else:
            self.statusBar().showMessage(self.tr("no_profiles_found"))

        self.setup_tray_icon()
        self.update_background_button_text()
        
        # ===== MEJORA #52: Inicializar dashboard =====
        if hasattr(self, 'dashboard_tab'):
            QTimer.singleShot(1000, self.update_dashboard_stats)
        
        # ===== MEJORA #56: Atajos de Teclado =====
        try:
            from keyboard_shortcuts import KeyboardShortcuts
            self.keyboard_shortcuts = KeyboardShortcuts(self)
        except ImportError:
            pass

        self._bind_multiple_mount_manager()

        # ===== MEJORA: Multi-Ventana (Ctrl+Shift+N) =====
        self.setup_multi_window_shortcut()

    def _setup_sidebar(self):
        """Configura la barra lateral izquierda con tipos de almacenamiento"""
        self.sidebar = Sidebar(self)
        self.sidebar.setFixedWidth(200)
        
        # Agregar tipos de almacenamiento
        self.sidebar.add_storage_type('vultr_s3', '🔷', 'Vultr S3', '#3498db')
        self.sidebar.add_storage_type('mega', '☁️', 'MEGA.nz', '#e74c3c')
        self.sidebar.add_storage_type('azure', '🔷', 'Azure Disks', '#0078D4')
        self.sidebar.add_storage_type('gcp', '☁️', 'Google Cloud', '#4285F4')
        
        # Conectar señal de selección
        self.sidebar.storage_selected.connect(self._on_sidebar_storage_selected)
        self.sidebar.add_storage_clicked.connect(self._on_add_storage_clicked)
        
        # Agregar al layout principal
        self.root_layout.insertWidget(0, self.sidebar)
    
    def _on_sidebar_storage_selected(self, storage_id: str):
        """Maneja la selección de tipo de almacenamiento desde la barra lateral"""
        if storage_id == 'vultr_s3':
            # Mostrar Stack 0 (Vultr)
            self.main_stack.setCurrentIndex(0)
            self._filter_profiles_by_type('vultr')
            self.statusBar().showMessage("🔷 Modo Vultr S3 activado")
            
        elif storage_id == 'mega':
            # Mostrar Stack 1 (MEGA)
            self.main_stack.setCurrentIndex(1)
            # MEGA Tab maneja sus propios perfiles internamente, o usamos filtro global si es compartido
            # La implementación actual de MegaTab parece autocontenida
            self.statusBar().showMessage("☁️ Modo MEGA.nz activado")
            
        elif storage_id == 'azure':
            # Mostrar Stack 2 (Azure)
            self.main_stack.setCurrentIndex(2)
            self.statusBar().showMessage("🔷 Modo Azure Disks activado")
            
        elif storage_id == 'gcp':
            # Mostrar Stack 3 (GCP)
            self.main_stack.setCurrentIndex(3)
            self.statusBar().showMessage("☁️ Modo Google Cloud Platform activado")
    
    def _filter_profiles_by_type(self, storage_type: str):
        """Filtra los perfiles en el selector según el tipo de almacenamiento"""
        self.profile_selector.blockSignals(True)
        self.profile_selector.clear()
        
        if storage_type == 'vultr':
            # Perfiles de Vultr S3 desde config_manager
            profiles = self.config_manager.list_profiles()
            for p in profiles:
                self.profile_selector.addItem(f"🔷 {p}")
        elif storage_type == 'mega':
            # Perfiles MEGA desde rclone_manager
            mega_profiles = self.rclone_manager.list_mega_profiles()
            for p in mega_profiles:
                self.profile_selector.addItem(f"☁️ {p['name']}")
        
        self.profile_selector.blockSignals(False)
        
        # Cargar el primer perfil si hay alguno
        if self.profile_selector.count() > 0:
            self.profile_selector.setCurrentIndex(0)
            display_name = self.profile_selector.currentText()
            self.load_profile(display_name)
    
    def _on_add_storage_clicked(self):
        """Muestra diálogo para agregar nuevo tipo de almacenamiento"""
        QMessageBox.information(
            self,
            "Próximamente",
            "La posibilidad de agregar nuevos tipos de almacenamiento "
            "(Google Drive, OneDrive, Dropbox, etc.) estará disponible pronto.\n\n"
            "Por ahora puedes:\n"
            "• Usar Vultr S3 (pestaña Principal)\n"
            "• Usar MEGA.nz (pestaña MEGA.nz)"
        )

    def setup_multi_window_shortcut(self):
        """Configura el atajo Ctrl+Shift+N para abrir nueva ventana"""
        from PyQt6.QtGui import QShortcut, QKeySequence
        self.new_window_shortcut = QShortcut(QKeySequence("Ctrl+Shift+N"), self)
        self.new_window_shortcut.activated.connect(self.open_new_window)

    def open_new_window(self):
        """Lanza una nueva instancia de la aplicación"""
        import subprocess
        import sys
        
        try:
            # Lanzar el mismo ejecutable/script como un proceso separado
            # DETACHED_PROCESS ensures it survives if parent dies (optional, but requested for resilience)
            # CREATE_NEW_PROCESS_GROUP is good practice
            flags = 0
            if sys.platform == 'win32':
                flags = subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS

            subprocess.Popen([sys.executable] + sys.argv, creationflags=flags)
            
            if LOGGING_AVAILABLE:
                logger.info("Nueva ventana lanzada por usuario (Ctrl+Shift+N)")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo abrir nueva ventana:\n{str(e)}")

    def _bind_multiple_mount_manager(self):
        """Preparar conexiones con MultipleMountManager"""
        try:
            self.multiple_mount_manager = MultipleMountManager(self.rclone_manager)
            self.multi_mounts_widget = MultiMountsWidget(self.multiple_mount_manager, self.translations)
            self.multi_mounts_widget.request_new_mount.connect(self.show_mount_tab)
            if hasattr(self, "mounts_content_layout") and self.multi_mounts_widget.parent() is None:
                insert_index = max(0, self.mounts_content_layout.count() - 1)
                self.mounts_content_layout.insertWidget(insert_index, self.multi_mounts_widget)
        except Exception as exc:
            if LOGGING_AVAILABLE:
                logger.error("No se pudo inicializar MultipleMountManager: %s", exc, exc_info=True)
            self.multiple_mount_manager = None
            self.multi_mounts_widget = None
            return

        self.multiple_mount_manager.refresh_all_status()
        self._refresh_multi_mounts_widget(refresh_manager=False, defer=True)

    def _refresh_multi_mounts_widget(self, refresh_manager=True, defer=False):
        manager = getattr(self, "multiple_mount_manager", None)
        widget = getattr(self, "multi_mounts_widget", None)
        if refresh_manager and manager:
            manager.refresh_all_status()
        if widget:
            if defer:
                QTimer.singleShot(0, widget.refresh_table)
            else:
                widget.refresh_table()

    def _auto_load_profile(self):
        """Cargar perfil automáticamente al iniciar"""
        if self.profile_selector.count() > 0:
            # Intentar cargar el último perfil activo
            last_profile = self.config_manager.get_active_profile()
            if last_profile:
                index = self.profile_selector.findText(last_profile)
                if index >= 0:
                    self.profile_selector.setCurrentIndex(index)
                    # load_profile se llama automáticamente por currentTextChanged
                else:
                    self.load_profile(self.profile_selector.currentText())
            else:
                self.load_profile(self.profile_selector.currentText())

            # Refrescar buckets automáticamente después de cargar perfil
            QTimer.singleShot(1000, self.refresh_buckets)
        
        # Verificar visibilidad del botón de cerrar sin desmontar al iniciar
        QTimer.singleShot(2000, self.update_close_without_unmount_button_visibility)

    def tr(self, key, *args):
        """Translate text using the translations system"""
        if self.translations:
            return self.translations.get(key, *args)
        return key

    def setup_top_controls(self):
        """Setup language and theme controls at the top"""
        top_layout = QHBoxLayout()
        
        # Language selector
        language_label = QLabel(self.tr("language"))
        self.language_button = QPushButton()
        self.language_button.setObjectName("languageButton")
        self.update_language_button_text()
        self.language_button.clicked.connect(self.show_language_menu)
        
        # Theme selector
        self.theme_button = QPushButton()
        self.theme_button.setObjectName("themeButton")
        self.update_theme_button_text()
        self.theme_button.clicked.connect(self.toggle_theme)

        # Send to background button (system tray quick action)
        self.background_button = QToolButton()
        self.background_button.setObjectName("backgroundButton")
        self.background_button.setAutoRaise(True)
        self.background_button.clicked.connect(lambda: self.send_to_tray(show_message=True))
        self.background_button.setToolTip(self.tr("send_to_background_tooltip"))
        self.update_background_button_text()
        
        # ===== MEJORA: Botón para cerrar sin desmontar unidades =====
        self.close_without_unmount_button = QPushButton(self.tr("close_without_unmount"))
        self.close_without_unmount_button.setObjectName("closeWithoutUnmountButton")
        self.close_without_unmount_button.setToolTip(self.tr("close_without_unmount_tooltip"))
        self.close_without_unmount_button.clicked.connect(self.close_without_unmounting)
        self.close_without_unmount_button.hide()  # Ocultar inicialmente
        
        top_layout.addWidget(language_label)
        top_layout.addWidget(self.language_button)
        top_layout.addStretch()
        top_layout.addWidget(self.theme_button)
        top_layout.addWidget(self.background_button)
        top_layout.addWidget(self.close_without_unmount_button)
        
        self.main_layout.addLayout(top_layout)

    def setup_tray_icon(self):
        """Configura el icono en la bandeja del sistema con menú mejorado"""
        if not QSystemTrayIcon.isSystemTrayAvailable():
            self.tray_icon = None
            return

        icon = self.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon)
        self.tray_icon = QSystemTrayIcon(icon, self)
        self._update_tray_tooltip()

        # ===== MENÚ CONTEXTUAL MEJORADO =====
        self._tray_menu = QMenu()
        self._tray_actions = {}

        # Acción: Mostrar ventana
        open_action = QAction(f"📂 {self.tr('tray_open')}", self)
        open_action.triggered.connect(self.restore_from_tray)
        self._tray_menu.addAction(open_action)
        self._tray_actions['open'] = open_action

        self._tray_menu.addSeparator()

        # Sección: Montar/Desmontar
        mount_action = QAction(f"➕ {self.tr('tray_mount_new_bucket')}", self)
        mount_action.triggered.connect(self.show_mount_tab)
        self._tray_menu.addAction(mount_action)
        self._tray_actions['mount'] = mount_action

        unmount_action = QAction(f"🗑 {self.tr('tray_unmount_all')}", self)
        unmount_action.triggered.connect(self.tray_unmount_all)
        self._tray_menu.addAction(unmount_action)
        self._tray_actions['unmount'] = unmount_action

        self._tray_menu.addSeparator()

        # Acción: Configuración
        settings_action = QAction(f"⚙️ {self.tr('tray_settings')}", self)
        settings_action.triggered.connect(self.open_settings)
        self._tray_menu.addAction(settings_action)
        self._tray_actions['settings'] = settings_action

        self._tray_menu.addSeparator()

        # Acción: Salir
        exit_action = QAction(f"❌ {self.tr('tray_exit')}", self)
        exit_action.triggered.connect(self.quit_application)
        self._tray_menu.addAction(exit_action)
        self._tray_actions['exit'] = exit_action

        self.tray_icon.setContextMenu(self._tray_menu)
        self.tray_icon.activated.connect(self._on_tray_activated)
        self.tray_icon.show()
        
        # ===== INICIALIZAR GESTOR DE NOTIFICACIONES =====
        self.notification_manager = NotificationManager(self.tray_icon, self.translations)
        
        # Notificar inicio de aplicación
        QTimer.singleShot(1000, lambda: self.notification_manager.notify_app_started())
    
    def _update_tray_tooltip(self):
        """Actualizar tooltip del icono en bandeja"""
        try:
            # from drive_detector import DriveDetector (Eliminado)
            detected = DriveDetector.detect_mounted_drives()
            mounted_count = len(detected) if detected else 0
            tooltip = self.tr("tray_tooltip").format(mounted_count)
        except:
            tooltip = self.tr("app_name")
        
        if self.tray_icon:
            self.tray_icon.setToolTip(tooltip)
    
    def show_mount_tab(self):
        """Mostrar ventana y cambiar a pestaña de montaje"""
        self.restore_from_tray()
        if hasattr(self, 'tabs'):
            # Cambiar a pestaña "Montar Disco" (índice 1)
            # Cambiar a pestaña "Montar Disco" (índice 1 en Vultr Tabs)
            self.main_stack.setCurrentIndex(0) # Asegurar que vemos Vultr
            self.vultr_tabs.setCurrentIndex(1)

    def update_language_button_text(self):
        """Update the language button text"""
        if self.translations:
            available_languages = self.translations.get_available_languages()
            current_lang = self.translations.current_language
            if current_lang in available_languages:
                self.language_button.setText(available_languages[current_lang])
            else:
                self.language_button.setText(self.tr("language"))

    def update_theme_button_text(self):
        """Update the theme button text"""
        if self.theme_manager:
            available_themes = self.theme_manager.get_available_themes()
            current_theme = self.theme_manager.current_theme
            if current_theme in available_themes:
                self.theme_button.setText(available_themes[current_theme])
            else:
                self.theme_button.setText(self.tr("theme"))

    def update_background_button_text(self):
        """Update the send-to-background button label"""
        if hasattr(self, 'background_button'):
            self.background_button.setText(self.tr("send_to_background"))
            self.background_button.setToolTip(self.tr("send_to_background_tooltip"))
        if hasattr(self, '_tray_actions') and self._tray_actions:
            if 'open' in self._tray_actions:
                self._tray_actions['open'].setText(f"📂 {self.tr('tray_open')}")
            if 'mount' in self._tray_actions:
                self._tray_actions['mount'].setText(f"➕ {self.tr('tray_mount_new_bucket')}")
            if 'unmount' in self._tray_actions:
                self._tray_actions['unmount'].setText(f"🗑 {self.tr('tray_unmount_all')}")
            if 'settings' in self._tray_actions:
                self._tray_actions['settings'].setText(f"⚙️ {self.tr('tray_settings')}")
            if 'exit' in self._tray_actions:
                self._tray_actions['exit'].setText(f"❌ {self.tr('tray_exit')}")
        if self.tray_icon:
            self.tray_icon.setToolTip(self.windowTitle())

    def send_to_tray(self, show_message=False):
        """Envía la aplicación a segundo plano"""
        if self.tray_icon:
            self.hide()
            self._is_in_tray = True
            if show_message:
                self.tray_icon.showMessage(
                    self.tr("background_running_title"),
                    self.tr("background_notification"),
                    QSystemTrayIcon.MessageIcon.Information,
                    4000
                )
        else:
            self.showMinimized()

    def restore_from_tray(self):
        """Restaurar la ventana principal desde la bandeja"""
        self.showNormal()
        self.activateWindow()
        self.raise_()
        self._is_in_tray = False

    def _on_tray_activated(self, reason):
        """Manejar la activación del icono en la bandeja"""
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            # Clic izquierdo: mostrar/ocultar ventana
            if self.isVisible():
                self.hide()
            else:
                self.restore_from_tray()
        elif reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            # Doble clic: siempre mostrar
            self.restore_from_tray()

    def tray_unmount_all(self):
        """Permitir desmontar unidades desde la bandeja"""
        self.restore_from_tray()
        QTimer.singleShot(100, self.unmount_all_detected_drives)

    def quit_application(self):
        """Salir completamente de la aplicación"""
        reply = QMessageBox.question(
            self,
            self.tr("confirm_exit_title"),
            self.tr("confirm_exit_text"),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Desmontar todas las unidades
            try:
                # from drive_detector import DriveDetector (Eliminado)
                DriveDetector.unmount_all_drives(self.translations)
            except:
                pass
            
            # Notificar
            if self.notification_manager:
                self.notification_manager.info(
                    self.tr("app_name"),
                    self.tr("closing_application")
                )
            
            # Marcar para salir realmente
            self._force_quit = True
            
            # Cerrar
            QApplication.quit()
    
    def close_without_unmounting(self):
        """Cerrar la aplicación sin desmontar las unidades montadas"""
        # Detener sincronización si está activa (pero no desmontar)
        if self.real_time_sync and self.real_time_sync.is_running():
            try:
                self.real_time_sync.stop()
                if LOGGING_AVAILABLE:
                    logger.info("Sincronización detenida antes de cerrar (sin desmontar)")
            except Exception as e:
                if LOGGING_AVAILABLE:
                    logger.warning(f"Error al detener sincronización: {e}")
        
        # Ocultar icono de bandeja si existe
        if self.tray_icon:
            try:
                self.tray_icon.hide()
            except:
                pass
        
        # Notificar
        if self.notification_manager:
            self.notification_manager.info(
                self.tr("app_name"),
                self.tr("close_without_unmount_message")
            )
        
        # Marcar para salir sin desmontar (evita el diálogo de "Drive Still Mounted")
        self._force_quit = True
        self._close_without_unmount = True  # Flag para evitar diálogo de desmontaje
        
        # Cerrar aplicación (las unidades permanecerán montadas)
        QApplication.quit()
    
    def exit_from_tray(self):
        """Cerrar la aplicación desde el menú de la bandeja (compatibilidad)"""
        self.quit_application()

    def _should_keep_in_background(self):
        """Determinar si la app debe quedarse en segundo plano"""
        sync_running = self.real_time_sync and self.real_time_sync.is_running()
        
        # Check GCP Sync
        if hasattr(self, 'gcp_tab') and hasattr(self.gcp_tab, 'sync_tab'):
             if getattr(self.gcp_tab.sync_tab, 'is_running', False):
                 sync_running = True

        drive_mounted = False
        try:
            drive_mounted = self.rclone_manager.is_mounted()
        except Exception:
            drive_mounted = False
            
        return sync_running or drive_mounted

    def _execute_shutdown_tasks(self):
        """Realizar tareas de limpieza antes de salir"""
        # Si se cerró sin desmontar, no mostrar diálogos
        if self._close_without_unmount:
            # Solo detener sincronización silenciosamente
            if self.real_time_sync and self.real_time_sync.is_running():
                try:
                    self.real_time_sync.stop()
                except:
                    pass
            
            if self.tray_icon:
                self.tray_icon.hide()
            return
        
        # Comportamiento normal (con diálogos)
        if self.real_time_sync and self.real_time_sync.is_running():
            reply = QMessageBox.question(
                self,
                self.tr("sync_running_title"),
                self.tr("sync_running_text"),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.Yes
            )

            if reply == QMessageBox.StandardButton.Yes:
                self.real_time_sync.stop()

        if self.rclone_manager.is_mounted():
            reply = QMessageBox.question(
                self,
                self.tr("drive_still_mounted_title"),
                self.tr("drive_still_mounted_text"),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.Yes
            )

            if reply == QMessageBox.StandardButton.Yes:
                self.rclone_manager.unmount_drive(self.drive_letter_input.currentText())

        if self.tray_icon:
            self.tray_icon.hide()

    def show_language_menu(self):
        """Show language selection menu"""
        if not self.translations:
            return
            
        menu = QMenu(self)
        available_languages = self.translations.get_available_languages()
        
        for lang_code, lang_name in available_languages.items():
            action = QAction(lang_name, self)
            action.setData(lang_code)
            action.triggered.connect(lambda checked, code=lang_code: self.change_language(code))
            
            # Mark current language
            if lang_code == self.translations.current_language:
                action.setCheckable(True)
                action.setChecked(True)
                
            menu.addAction(action)
        
        menu.exec(self.language_button.mapToGlobal(self.language_button.rect().bottomLeft()))

    def change_language(self, language_code):
        """Change the application language"""
        if self.translations and self.translations.set_language(language_code):
            # Save preference
            if self.save_preferences_callback:
                preferences = {
                    "language": language_code,
                    "theme": self.theme_manager.current_theme if self.theme_manager else "dark"
                }
                self.save_preferences_callback(preferences)
            
            # Show restart message
            QMessageBox.information(
                self, 
                self.tr("language_changed_title"), 
                self.tr("language_changed_message").format(
                    self.translations.get_available_languages()[language_code]
                )
            )
            
            # Update button text
            self.update_language_button_text()
            self.update_background_button_text()
            if getattr(self, "multi_mounts_widget", None):
                self.multi_mounts_widget.update_translations()

    def toggle_theme(self):
        """Toggle between dark and light theme"""
        if not self.theme_manager:
            return
            
        new_theme = "light" if self.theme_manager.current_theme == "dark" else "dark"
        
        if self.theme_manager.set_theme(new_theme):
            # Apply new theme
            if hasattr(self, 'parent') and hasattr(self.parent(), 'setStyleSheet'):
                self.parent().setStyleSheet(self.theme_manager.get_current_stylesheet())
            else:
                from PyQt6.QtWidgets import QApplication
                QApplication.instance().setStyleSheet(self.theme_manager.get_current_stylesheet())
            
            # Save preference
            if self.save_preferences_callback:
                preferences = {
                    "language": self.translations.current_language if self.translations else "en",
                    "theme": new_theme
                }
                self.save_preferences_callback(preferences)
            
            # Update button text
            self.update_theme_button_text()

    def setup_main_tab(self):
        # Crear un scroll area para toda la pestaña
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        
        # Widget contenedor para el scroll
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setSpacing(15)
        layout.setContentsMargins(10, 10, 10, 10)
        self.mounts_content_layout = layout

        # Profile selection group
        profile_group = QGroupBox(self.tr("profile_selection"))
        profile_layout = QHBoxLayout()
        self.profile_label = QLabel(self.tr("active_profile"))
        self.profile_selector = QComboBox()
        self.profile_selector = QComboBox()
        # self.profile_selector.addItems(self.config_manager.list_profiles()) # Replaced by refresh_profiles_list
        self.refresh_profiles_list()
        self.profile_selector.currentTextChanged.connect(self.load_profile)
        profile_layout.addWidget(self.profile_label)
        profile_layout.addWidget(self.profile_selector, 1)
        profile_group.setLayout(profile_layout)
        layout.addWidget(profile_group)

        # Bucket selection group
        bucket_group = QGroupBox(self.tr("bucket_selection"))
        bucket_layout = QHBoxLayout()
        self.bucket_label = QLabel(self.tr("select_bucket"))
        self.bucket_selector = QComboBox()
        self.refresh_buckets_btn = QPushButton(self.tr("refresh"))
        self.refresh_buckets_btn.clicked.connect(lambda: self.refresh_buckets(force_remote=True))
        bucket_layout.addWidget(self.bucket_label)
        bucket_layout.addWidget(self.bucket_selector, 1)
        bucket_layout.addWidget(self.refresh_buckets_btn)
        bucket_group.setLayout(bucket_layout)
        layout.addWidget(bucket_group)
        
        # ===== NUEVO: Bucket Management Buttons =====
        bucket_mgmt_group = QGroupBox("🗂️ Gestión de Buckets")
        bucket_mgmt_layout = QHBoxLayout()
        
        self.create_bucket_btn = QPushButton("➕ Crear Bucket")
        self.create_bucket_btn.clicked.connect(self.create_bucket)
        self.create_bucket_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                font-weight: bold;
                padding: 10px 20px;
                border-radius: 5px;
            }
            QPushButton:hover { background-color: #229954; }
        """)
        
        self.delete_bucket_btn = QPushButton("🗑️ Eliminar Bucket")
        self.delete_bucket_btn.clicked.connect(self.delete_bucket)
        self.delete_bucket_btn.setEnabled(False)  # Solo si hay bucket seleccionado
        self.delete_bucket_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                font-weight: bold;
                padding: 10px 20px;
                border-radius: 5px;
            }
            QPushButton:hover { background-color: #c0392b; }
            QPushButton:disabled { background-color: #95a5a6; }
        """)
        
        bucket_mgmt_layout.addWidget(self.create_bucket_btn)
        bucket_mgmt_layout.addWidget(self.delete_bucket_btn)
        bucket_mgmt_group.setLayout(bucket_mgmt_layout)
        layout.addWidget(bucket_mgmt_group)
        
        # Habilitar botón de eliminar solo si hay bucket seleccionado
        self.bucket_selector.currentTextChanged.connect(
            lambda text: self.delete_bucket_btn.setEnabled(bool(text))
        )

        # Main action buttons
        actions_group = QGroupBox(self.tr("actions"))
        actions_layout = QVBoxLayout()
        
        buttons_layout = QHBoxLayout()
        self.upload_button = QPushButton(self.tr("upload_file"))
        self.upload_button.clicked.connect(self.upload_file)
        self.backup_button = QPushButton(self.tr("backup_folder"))
        self.backup_button.clicked.connect(self.full_backup)
        buttons_layout.addWidget(self.upload_button)
        buttons_layout.addWidget(self.backup_button)
        
        actions_layout.addLayout(buttons_layout)
        actions_group.setLayout(actions_layout)
        layout.addWidget(actions_group)

        # Settings button
        settings_layout = QHBoxLayout()
        self.settings_button = QPushButton(self.tr("manage_profiles"))
        self.settings_button.clicked.connect(self.open_settings)
        settings_layout.addStretch()
        settings_layout.addWidget(self.settings_button)
        layout.addLayout(settings_layout)

        layout.addStretch()
        
        # Configurar el scroll area
        scroll.setWidget(container)
        
        # Agregar el scroll area al tab
        tab_layout = QVBoxLayout(self.main_tab)
        tab_layout.setContentsMargins(0, 0, 0, 0)
        tab_layout.addWidget(scroll)

    def setup_mount_tab(self):
        # Crear un scroll area para toda la pestaña
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        
        # Widget contenedor para el scroll
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setSpacing(15)
        layout.setContentsMargins(10, 10, 10, 10)

        # Detector de discos montados (NUEVO)
        detector_group = QGroupBox("🔍 " + self.tr("mounted_drives_detector"))
        detector_group.setObjectName("detector_group")  # Nombre para encontrarlo después
        detector_group.setToolTip("ℹ️ " + self.tr("detector_tooltip"))  # Tooltip informativo
        detector_layout = QVBoxLayout()
        
        detector_info = QLabel(self.tr("detector_info"))
        detector_info.setWordWrap(True)
        detector_info.setStyleSheet("color: #888; font-size: 10pt; margin-bottom: 10px;")
        detector_layout.addWidget(detector_info)
        
        detector_buttons_layout = QHBoxLayout()
        self.detect_drives_btn = QPushButton("🔎 " + self.tr("detect_mounted_drives"))
        self.detect_drives_btn.clicked.connect(self.detect_mounted_drives)
        self.detect_drives_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px 20px;
                font-size: 11pt;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        
        self.unmount_all_btn = QPushButton("🗑️ " + self.tr("unmount_all_drives"))
        self.unmount_all_btn.clicked.connect(self.unmount_all_detected_drives)
        self.unmount_all_btn.setEnabled(False)
        self.unmount_all_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 10px 20px;
                font-size: 11pt;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
            }
        """)
        
        detector_buttons_layout.addWidget(self.detect_drives_btn)
        detector_buttons_layout.addWidget(self.unmount_all_btn)
        detector_layout.addLayout(detector_buttons_layout)
        
        # Lista de unidades detectadas
        self.drives_list = QTextEdit()
        self.drives_list.setReadOnly(True)
        self.drives_list.setMinimumHeight(70)  # Muy pequeño, solo para el texto
        self.drives_list.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)  # Solo crece verticalmente si hay contenido
        self.drives_list.setPlainText(self.tr("no_drives_detected"))
        self.drives_list.setStyleSheet("""
            QTextEdit {
                background-color: #2c3e50;
                color: #ecf0f1;
                border: 2px solid #34495e;
                border-radius: 5px;
                padding: 10px;
                font-family: 'Consolas', monospace;
                font-size: 10pt;
            }
        """)
        detector_layout.addWidget(self.drives_list)
        
        # Contenedor para botones individuales de desmontaje (se llena dinámicamente)
        self.individual_buttons_container = QWidget()
        self.individual_buttons_container_layout = QVBoxLayout(self.individual_buttons_container)
        self.individual_buttons_container_layout.setContentsMargins(0, 10, 0, 0)
        self.individual_buttons_container.hide()  # Oculto hasta que se detecten unidades
        detector_layout.addWidget(self.individual_buttons_container)
        
        detector_group.setLayout(detector_layout)
        layout.addWidget(detector_group)

        # Mount configuration
        mount_group = QGroupBox(self.tr("mount_configuration"))
        mount_group.setToolTip("ℹ️ " + self.tr("mount_config_tooltip"))  # Tooltip informativo
        mount_layout = QVBoxLayout()

        # Plan Selection Logic
        plan_layout = QHBoxLayout()
        plan_layout.addWidget(QLabel("🚀 " + self.tr("performance_plan") + ":"))
        
        self.mount_plan_selector = QComboBox()
        self.mount_plan_selector.setToolTip(self.tr("select_performance_plan_tooltip"))
        plan_layout.addWidget(self.mount_plan_selector, 1)
        
        self.edit_mount_plans_btn = QPushButton("⚙️")
        self.edit_mount_plans_btn.setToolTip(self.tr("edit_plans"))
        self.edit_mount_plans_btn.setFixedWidth(40)
        self.edit_mount_plans_btn.clicked.connect(self.open_mount_plan_editor)
        plan_layout.addWidget(self.edit_mount_plans_btn)
        
        mount_layout.addLayout(plan_layout)

        # Cargar planes iniciales
        self.load_mount_plans()

        drive_letter_layout = QHBoxLayout()
        drive_letter_layout.addWidget(QLabel(self.tr("drive_letter")))
        self.drive_letter_input = QComboBox()
        available_drives = [chr(i) for i in range(ord('V'), ord('Z')+1)]
        self.drive_letter_input.addItems(available_drives)
        # ✅ CONECTAR: Cuando cambia la letra, refrescar si está montada
        self.drive_letter_input.currentTextChanged.connect(self.update_unmount_button_state)
        drive_letter_layout.addWidget(self.drive_letter_input)
        drive_letter_layout.addStretch()
        mount_layout.addLayout(drive_letter_layout)

        mount_group.setLayout(mount_layout)
        layout.addWidget(mount_group)

        # Mount actions
        actions_group = QGroupBox(self.tr("drive_actions"))
        actions_group.setToolTip("ℹ️ " + self.tr("mount_actions_tooltip"))  # Tooltip informativo
        actions_layout = QVBoxLayout()

        self.mount_status_label = QLabel(self.tr("status_not_mounted"))
        actions_layout.addWidget(self.mount_status_label)

        buttons_layout = QHBoxLayout()
        self.mount_button = QPushButton(self.tr("mount_drive"))
        self.mount_button.clicked.connect(self.mount_drive)

        self.open_drive_button = QPushButton(self.tr("open_drive"))
        self.open_drive_button.setEnabled(False)
        self.open_drive_button.setToolTip(self.tr("open_drive_tooltip"))
        self.open_drive_button.clicked.connect(self.open_drive)
        self.open_drive_button.setStyleSheet("""
            QPushButton {
                background-color: #2980b9;
                color: white;
                border: none;
                padding: 10px 20px;
                font-size: 11pt;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #1f6391;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
            }
        """)

        self.unmount_button = QPushButton(self.tr("unmount_drive"))
        self.unmount_button.clicked.connect(self.unmount_drive)
        self.unmount_button.setEnabled(False)

        buttons_layout.addWidget(self.mount_button)
        buttons_layout.addWidget(self.open_drive_button)
        buttons_layout.addWidget(self.unmount_button)

        actions_layout.addLayout(buttons_layout)
        actions_group.setLayout(actions_layout)
        layout.addWidget(actions_group)

        # Info text
        info_group = QGroupBox(self.tr("information"))
        info_layout = QVBoxLayout()
        info_text = QTextEdit()
        info_text.setReadOnly(True)
        info_text.setMinimumHeight(80)
        info_text.setMaximumHeight(160)
        info_text.setPlainText(self.tr("mount_info").replace('\\n', '\n'))
        info_layout.addWidget(info_text)
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)

        layout.addStretch()
        
        # Configurar el scroll area
        scroll.setWidget(container)
        
        # Agregar el scroll area al tab
        tab_layout = QVBoxLayout(self.mount_tab)
        tab_layout.setContentsMargins(0, 0, 0, 0)
        tab_layout.addWidget(scroll)



    def setup_sync_tab(self):
        # Crear un scroll area para toda la pestaña
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        
        # Widget contenedor para el scroll
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setSpacing(15)
        layout.setContentsMargins(10, 10, 10, 10)

        # Folder selection
        folder_group = QGroupBox(self.tr("folder_to_monitor"))
        folder_group.setToolTip("ℹ️ " + self.tr("folder_monitor_tooltip"))  # Tooltip informativo
        folder_layout = QVBoxLayout()

        folder_select_layout = QHBoxLayout()
        self.sync_folder_label = QLabel(self.tr("no_folder_selected"))
        self.sync_folder_label.setWordWrap(True)
        self.sync_folder_btn = QPushButton(self.tr("select_folder"))
        self.sync_folder_btn.clicked.connect(self.select_sync_folder)
        folder_select_layout.addWidget(self.sync_folder_label, 1)
        folder_select_layout.addWidget(self.sync_folder_btn)
        folder_layout.addLayout(folder_select_layout)

        folder_group.setLayout(folder_layout)
        layout.addWidget(folder_group)

        # Sync status and controls
        sync_group = QGroupBox(self.tr("sync_control"))
        sync_group.setToolTip("ℹ️ " + self.tr("sync_control_tooltip"))  # Tooltip informativo
        sync_layout = QVBoxLayout()

        self.sync_status_label = QLabel(self.tr("status_stopped"))
        sync_layout.addWidget(self.sync_status_label)

        buttons_layout = QHBoxLayout()
        self.start_sync_btn = QPushButton(self.tr("start_sync"))
        self.start_sync_btn.clicked.connect(self.start_real_time_sync)
        self.stop_sync_btn = QPushButton(self.tr("stop_sync"))
        self.stop_sync_btn.clicked.connect(self.stop_real_time_sync)
        self.stop_sync_btn.setEnabled(False)
        buttons_layout.addWidget(self.start_sync_btn)
        buttons_layout.addWidget(self.stop_sync_btn)

        sync_layout.addLayout(buttons_layout)
        sync_group.setLayout(sync_layout)
        layout.addWidget(sync_group)

        # Activity log
        log_group = QGroupBox(self.tr("activity_log"))
        log_group.setToolTip("ℹ️ " + self.tr("activity_log_tooltip"))  # Tooltip informativo
        log_layout = QVBoxLayout()

        self.sync_log = QTextEdit()
        self.sync_log.setReadOnly(True)
        self.sync_log.setMaximumHeight(200)
        self.sync_log.setPlainText(self.tr("sync_not_started"))
        log_layout.addWidget(self.sync_log)

        clear_log_btn = QPushButton(self.tr("clear_log"))
        clear_log_btn.clicked.connect(lambda: self.sync_log.clear())
        log_layout.addWidget(clear_log_btn)

        log_group.setLayout(log_layout)
        layout.addWidget(log_group)

        # Info text
        info_group = QGroupBox(self.tr("information"))
        info_layout = QVBoxLayout()
        info_text = QTextEdit()
        info_text.setReadOnly(True)
        info_text.setMinimumHeight(80)
        info_text.setMaximumHeight(160)
        info_text.setPlainText(self.tr("sync_info"))
        info_layout.addWidget(info_text)
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)

        layout.addStretch()
        
        # Configurar el scroll area
        scroll.setWidget(container)
        
        # Agregar el scroll area al tab
        tab_layout = QVBoxLayout(self.sync_tab)
        tab_layout.setContentsMargins(0, 0, 0, 0)
        tab_layout.addWidget(scroll)

    def select_sync_folder(self):
        """Select folder for real-time synchronization"""
        folder = QFileDialog.getExistingDirectory(self, self.tr("dialog_select_monitor_folder"))
        if folder:
            self.sync_folder_label.setText(folder)
            self.sync_folder_label.setProperty('folder_path', folder)

    def start_real_time_sync(self):
        """Start real-time synchronization"""
        if not self.s3_handler:
            QMessageBox.warning(self, self.tr("warning"), self.tr("select_profile_first"))
            return

        if self.bucket_selector.count() == 0:
            QMessageBox.warning(self, self.tr("warning"), self.tr("select_bucket_first"))
            return

        folder = self.sync_folder_label.property('folder_path')
        if not folder:
            QMessageBox.warning(self, self.tr("warning"), self.tr("select_folder_to_monitor"))
            return

        bucket_name = self.bucket_selector.currentText()
        
        self.real_time_sync = RealTimeSync(
            self.s3_handler,
            bucket_name,
            folder,
            self.sync_log_message
        )

        success, message = self.real_time_sync.start()

        if success:
            self.sync_status_label.setText(self.tr("status_monitoring_folder").format(folder))
            self.start_sync_btn.setEnabled(False)
            self.stop_sync_btn.setEnabled(True)
            self.sync_log_message(f"✓ {message}")
            QMessageBox.information(self, self.tr("success"), message)
        else:
            QMessageBox.critical(self, self.tr("error"), message)
            self.sync_log_message(f"✗ {message}")

    def stop_real_time_sync(self):
        """Stop real-time synchronization"""
        if self.real_time_sync:
            success, message = self.real_time_sync.stop()
            
            if success:
                self.sync_status_label.setText(self.tr('status_stopped'))
                self.start_sync_btn.setEnabled(True)
                self.stop_sync_btn.setEnabled(False)
                self.sync_log_message(f"✓ {message}")
            else:
                QMessageBox.critical(self, self.tr("error"), message)
                self.sync_log_message(f"✗ {message}")

    def sync_log_message(self, message):
        """Add message to sync log"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.sync_log.append(f"[{timestamp}] {message}")

    def setup_advanced_tab(self):
        # Crear un scroll area para toda la pestaña
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        
        # Widget contenedor para el scroll
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setSpacing(15)
        layout.setContentsMargins(10, 10, 10, 10)

        # Warning label
        warning_label = QLabel(f"⚠️ {self.tr('advanced_warning')}")
        warning_label.setStyleSheet("font-weight: bold; color: #ff6b6b; font-size: 12pt;")
        layout.addWidget(warning_label)

        # Format bucket group
        format_group = QGroupBox(self.tr('bucket_management'))
        format_layout = QVBoxLayout()

        format_info = QLabel(self.tr('format_warning'))
       
        format_info.setWordWrap(True)
        format_layout.addWidget(format_info)

        self.format_button = QPushButton(f"🗑️ {self.tr('format_bucket')}")
        self.format_button.clicked.connect(self.format_bucket)
        self.format_button.setStyleSheet(
            "QPushButton { background-color: #c92a2a; }"
            "QPushButton:hover { background-color: #a51e1e; }"
        )
        format_layout.addWidget(self.format_button)

        format_group.setLayout(format_layout)
        layout.addWidget(format_group)

        layout.addStretch()
        
        # Configurar el scroll area
        scroll.setWidget(container)
        
        # Agregar el scroll area al tab
        tab_layout = QVBoxLayout(self.advanced_tab)
        tab_layout.setContentsMargins(0, 0, 0, 0)
        tab_layout.addWidget(scroll)

    def refresh_buckets(self, force_remote=False):
        if not self.s3_handler:
            self.statusBar().showMessage(self.tr("select_profile_first"))
            return

        if force_remote and self.s3_handler:
            self.s3_handler.clear_cache('list_buckets')

        if self._refreshing_buckets and self._current_bucket_handler is self.s3_handler and not force_remote:
            if LOGGING_AVAILABLE:
                logger.debug("Se ignoró refresh_buckets porque ya hay una operación en curso.")
            return

        self._refreshing_buckets = True
        self._current_bucket_handler = self.s3_handler
        self.bucket_selector.clear()
        self.statusBar().showMessage(self.tr("loading_buckets"))

        current_handler = self.s3_handler
        description = f"list_buckets[{getattr(current_handler, 'host_base', 'unknown')}]"

        def fetch():
            return current_handler.list_buckets(use_cache=not force_remote)

        def on_success(result):
            if current_handler is not self.s3_handler:
                if LOGGING_AVAILABLE:
                    logger.debug("Resultado de buckets descartado: handler cambió durante la operación.")
                return
            buckets, error_message = result
            self._handle_bucket_response(buckets, error_message, force_remote=force_remote)

        def on_error(exc):
            if current_handler is not self.s3_handler:
                return
            error_msg = f"Error inesperado al listar buckets: {exc}"
            if LOGGING_AVAILABLE:
                logger.error("Error listando buckets (%s): %s", description, str(exc), exc_info=True)
            self._handle_bucket_response([], error_msg, force_remote=force_remote)

        def on_finished():
            self._refreshing_buckets = False
            self._current_bucket_handler = None

        self.task_runner.run(
            fetch,
            on_success=on_success,
            on_error=on_error,
            on_finished=on_finished,
            description=description,
        )

    def _handle_bucket_response(self, buckets, error_message, force_remote=False):
        self.bucket_selector.clear()
        if hasattr(self, 'tools_tab'):
            self.tools_tab.set_buckets(buckets if buckets else [])

        if error_message:
            short_error = error_message if len(error_message) <= 120 else f"{error_message[:117]}..."
            self.statusBar().showMessage(f"❌ {short_error}")

            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setWindowTitle(self.tr("error_list_buckets_title"))
            msg.setText(self.tr("error_list_buckets_text"))
            msg.setDetailedText(error_message)
            msg.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg.exec()

            if LOGGING_AVAILABLE:
                logger.error(f"Error al refrescar buckets: {error_message}")
        elif buckets:
            self.bucket_selector.addItems(buckets)
            self.statusBar().showMessage(self.tr("buckets_found").format(len(buckets)))
            if LOGGING_AVAILABLE:
                logger.info(f"Buckets cargados exitosamente: {len(buckets)}")
        else:
            self.statusBar().showMessage(self.tr("no_buckets_found"))
            if LOGGING_AVAILABLE:
                logger.info("No se encontraron buckets (puede ser normal si no hay buckets creados)")

        if isinstance(force_remote, bool) and force_remote:
            # Invalidar caché de tamaños para obtener datos frescos del bucket activo
            if self.s3_handler:
                self.s3_handler.clear_cache('get_bucket_size')

        # Actualizar dashboard con métricas posiblemente nuevas
        self.update_dashboard_stats(force_remote=force_remote)

    def refresh_profiles_list(self):
        """Refresh the list of available profiles (Vultr + MEGA)"""
        current = self.profile_selector.currentText()
        self.profile_selector.blockSignals(True)
        self.profile_selector.clear()
        
        # 1. Vultr Profiles
        vultr_profiles = self.config_manager.list_profiles()
        for p in vultr_profiles:
             self.profile_selector.addItem(f"🔷 {p}", p) # Store real name in data

        # 2. MEGA Profiles
        mega_profiles = self.rclone_manager.list_mega_profiles()
        for p in mega_profiles:
            self.profile_selector.addItem(f"☁️ {p['name']}", p['name'])

        self.profile_selector.blockSignals(False)
        
        # Restore selection if possible
        if current:
            # Try to find exact match or match in data
            index = self.profile_selector.findData(current)
            if index < 0:
                 # Try to find by text (maybe user had "🔷 Profile")
                 index = self.profile_selector.findText(current)
            
            if index >= 0:
                self.profile_selector.setCurrentIndex(index)

    def load_profile(self, display_name):
        # Get real profile name from data if available
        index = self.profile_selector.currentIndex()
        if index >= 0:
            profile_name = self.profile_selector.itemData(index)
        else:
            profile_name = display_name
            
        if not profile_name:
            self.s3_handler = None
            self.statusBar().showMessage(self.tr("no_profile_selected"))
            return
            
        # Guardar como perfil activo
        self.config_manager.set_active_profile(profile_name)

        # 1. Check if it is a MEGA profile
        mega_profiles = [p['name'] for p in self.rclone_manager.list_mega_profiles()]
        if profile_name in mega_profiles:
            self.s3_handler = None
            self._current_profile_type = 'mega'  # Track profile type
            self._current_mega_profile = profile_name
            self.statusBar().showMessage(f"☁️ Perfil MEGA '{profile_name}' cargado.")
            
            # Setup UI for MEGA (No buckets needed, just Root)
            self.bucket_selector.blockSignals(True)
            self.bucket_selector.clear()
            self.bucket_selector.addItem("/ (Raíz)")
            self.bucket_selector.setEnabled(False)
            self.refresh_buckets_btn.setEnabled(False)
            self.create_bucket_btn.setEnabled(False)
            self.delete_bucket_btn.setEnabled(False)
            self.bucket_selector.blockSignals(False)
            
            # Enable file operations (will use rclone instead of S3)
            self.upload_button.setEnabled(True) 
            self.backup_button.setEnabled(True)
            return

        # 2. It is a Vultr S3 Profile
        self._current_profile_type = 'vultr'
        self._current_mega_profile = None
        # Re-enable UI elements
        self.bucket_selector.setEnabled(True)
        self.refresh_buckets_btn.setEnabled(True)
        self.create_bucket_btn.setEnabled(True)
        # delete button depends on selection
        self.upload_button.setEnabled(True)
        self.backup_button.setEnabled(True)

        config = self.config_manager.get_config(profile_name)
        if config:
            try:
                # Validar que las credenciales no estén vacías
                access_key = config.get('access_key', '').strip()
                secret_key = config.get('secret_key', '').strip()
                host_base = config.get('host_base', '').strip()
                
                if not access_key or not secret_key:
                    error_msg = self.tr("profile_credentials_empty")
                    self.statusBar().showMessage(f"❌ {error_msg}")
                    if LOGGING_AVAILABLE:
                        logger.error(f"Perfil '{profile_name}' tiene credenciales vacías")
                    
                    from PyQt6.QtWidgets import QMessageBox
                    QMessageBox.warning(self, self.tr("warning"), error_msg)
                    return
                
                if not host_base:
                    error_msg = self.tr("profile_host_empty")
                    self.statusBar().showMessage(f"❌ {error_msg}")
                    if LOGGING_AVAILABLE:
                        logger.error(f"Perfil '{profile_name}' tiene host_base vacío")
                    
                    from PyQt6.QtWidgets import QMessageBox
                    QMessageBox.warning(self, self.tr("warning"), error_msg)
                    return
                
                # Intentar crear el handler
                self.s3_handler = S3Handler(access_key, secret_key, host_base)
                self.statusBar().showMessage(self.tr("profile_loaded").format(profile_name))
                
                if LOGGING_AVAILABLE:
                    logger.info(f"Perfil '{profile_name}' cargado exitosamente")
                
                # Refrescar buckets
                self.refresh_buckets()
                
            except ValueError as e:
                # Error de validación (credenciales vacías, etc.)
                error_msg = str(e)
                self.statusBar().showMessage(f"❌ {error_msg}")
                if LOGGING_AVAILABLE:
                    logger.error(f"Error al cargar perfil '{profile_name}': {error_msg}")
                
                from PyQt6.QtWidgets import QMessageBox
                QMessageBox.warning(self, self.tr("profile_load_error_title"), error_msg)
                self.s3_handler = None
                
            except Exception as e:
                # Otros errores
                error_msg = self.tr("profile_load_unexpected_error").format(str(e))
                self.statusBar().showMessage(f"❌ {error_msg}")
                if LOGGING_AVAILABLE:
                    logger.error(f"Error inesperado al cargar perfil '{profile_name}': {str(e)}", exc_info=True)
                
                if ERROR_HANDLING_AVAILABLE:
                    error = handle_error(e, context="load_profile")
                    from PyQt6.QtWidgets import QMessageBox
                    QMessageBox.warning(self, self.tr("profile_load_error_title"), error.message)
                else:
                    from PyQt6.QtWidgets import QMessageBox
                    QMessageBox.warning(self, self.tr("profile_load_error_title"), error_msg)
                self.s3_handler = None
        else:
            error_msg = self.tr("profile_not_found").format(profile_name)
            self.statusBar().showMessage(f"❌ {error_msg}")
            if LOGGING_AVAILABLE:
                logger.error(error_msg)
            self.s3_handler = None

    def upload_file(self):
        # Check if using MEGA profile
        if getattr(self, '_current_profile_type', None) == 'mega':
            file_path, _ = QFileDialog.getOpenFileName(self, self.tr("dialog_select_upload_file"))
            if file_path:
                profile_name = self._current_mega_profile
                self.statusBar().showMessage(self.tr("status_uploading_file").format(os.path.basename(file_path)))
                self.progress_bar.setVisible(True)
                self.progress_bar.setValue(0)
                
                # Use rclone to copy file to MEGA
                def do_upload():
                    return self.rclone_manager.copy_file_to_remote(profile_name, file_path, "/")
                
                def on_success(result):
                    self.progress_bar.setVisible(False)
                    success, msg = result
                    if success:
                        QMessageBox.information(self, self.tr("success"), f"Archivo '{os.path.basename(file_path)}' subido a MEGA.")
                        self.statusBar().showMessage(self.tr("status_upload_completed"), 5000)
                    else:
                        QMessageBox.warning(self, self.tr("error"), f"Error: {msg}")
                        self.statusBar().showMessage(self.tr("status_upload_failed"), 5000)
                
                def on_error(exc):
                    self.progress_bar.setVisible(False)
                    QMessageBox.warning(self, self.tr("error"), str(exc))
                
                self.task_runner.run(do_upload, on_success=on_success, on_error=on_error, description="mega_upload")
            return
        
        # Original S3 upload logic
        if not self.s3_handler:
            QMessageBox.warning(self, self.tr("warning"), self.tr("select_profile_first"))
            return

        if self.bucket_selector.count() == 0:
            QMessageBox.warning(self, self.tr("warning"), self.tr("no_buckets_available"))
            return
        
        file_path, _ = QFileDialog.getOpenFileName(self, self.tr("dialog_select_upload_file"))
        if file_path:
            bucket_name = self.bucket_selector.currentText()
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)
            self.statusBar().showMessage(self.tr("status_uploading_file").format(os.path.basename(file_path)))
            
            self.upload_thread = UploadThread(self.s3_handler, bucket_name, file_path)
            self.upload_thread.finished.connect(self.upload_finished)
            self.upload_thread.start()

    def upload_finished(self, success, payload):
        self.progress_bar.setVisible(False)
        payload = payload or {}
        file_name = payload.get("file")
        error_detail = payload.get("error")

        if success:
            if file_name:
                QMessageBox.information(
                    self,
                    self.tr("success"),
                    self.tr("upload_success_dialog").format(file_name),
                )
            else:
                QMessageBox.information(self, self.tr("success"), self.tr("status_upload_completed"))
            self.statusBar().showMessage(self.tr("status_upload_completed"), 5000)
        else:
            if file_name:
                message = self.tr("upload_error_dialog").format(
                    file_name,
                    error_detail or "",
                )
            else:
                message = error_detail or self.tr("status_upload_failed")
            QMessageBox.critical(self, self.tr("error"), message)
            self.statusBar().showMessage(self.tr("status_upload_failed"), 5000)

    def full_backup(self):
        # Check if using MEGA profile
        if getattr(self, '_current_profile_type', None) == 'mega':
            dir_path = QFileDialog.getExistingDirectory(self, self.tr("dialog_select_backup_directory"))
            if dir_path:
                profile_name = self._current_mega_profile
                self.statusBar().showMessage(self.tr("status_backup_starting").format(dir_path))
                self.progress_bar.setVisible(True)
                self.progress_bar.setValue(0)
                
                # Use rclone to copy folder to MEGA
                def do_backup():
                    return self.rclone_manager.copy_folder_to_remote(profile_name, dir_path, "/")
                
                def on_success(result):
                    self.progress_bar.setVisible(False)
                    success, msg = result
                    if success:
                        QMessageBox.information(self, self.tr("success"), f"Carpeta '{os.path.basename(dir_path)}' respaldada a MEGA.")
                        self.statusBar().showMessage(self.tr("status_backup_completed"), 5000)
                    else:
                        QMessageBox.warning(self, self.tr("error"), f"Error: {msg}")
                        self.statusBar().showMessage(self.tr("status_backup_failed"), 5000)
                
                def on_error(exc):
                    self.progress_bar.setVisible(False)
                    QMessageBox.warning(self, self.tr("error"), str(exc))
                
                self.task_runner.run(do_backup, on_success=on_success, on_error=on_error, description="mega_backup")
            return
        
        # Original S3 backup logic
        if not self.s3_handler:
            QMessageBox.warning(self, self.tr("warning"), self.tr("select_profile_first"))
            return

        if self.bucket_selector.count() == 0:
            QMessageBox.warning(self, self.tr("warning"), self.tr("no_buckets_available"))
            return
        
        dir_path = QFileDialog.getExistingDirectory(self, self.tr("dialog_select_backup_directory"))
        if dir_path:
            bucket_name = self.bucket_selector.currentText()
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)
            self.statusBar().showMessage(self.tr("status_backup_starting").format(dir_path))
            
            self.backup_thread = BackupThread(self.s3_handler, bucket_name, dir_path)
            self.backup_thread.progress.connect(self.backup_progress)
            self.backup_thread.finished.connect(self.backup_finished)
            self.backup_thread.start()

    def backup_progress(self, value, payload):
        self.progress_bar.setValue(value)
        payload = payload or {}
        current = payload.get("current")
        total = payload.get("total")
        file_path = payload.get("file")
        if current and total and file_path:
            self.statusBar().showMessage(
                self.tr("status_backup_progress").format(current, total, file_path)
            )
        elif file_path:
            self.statusBar().showMessage(self.tr("status_backup_progress_simple").format(file_path))

    def backup_finished(self, success, payload):
        self.progress_bar.setVisible(False)
        payload = payload or {}
        if success:
            total = payload.get("total", 0)
            QMessageBox.information(
                self,
                self.tr("success"),
                self.tr("backup_success_dialog").format(total),
            )
            self.statusBar().showMessage(self.tr("status_backup_completed"), 5000)
        else:
            reason = payload.get("reason")
            if reason == "no_files":
                message = self.tr("backup_no_files")
            elif reason == "exception":
                detail = payload.get("detail", "")
                message = self.tr("backup_error_dialog").format(detail)
            else:
                message = self.tr("status_backup_failed")
            QMessageBox.critical(self, self.tr("error"), message)
            self.statusBar().showMessage(self.tr("status_backup_failed"), 5000)

    def load_mount_plans(self):
        """Load available plans into the mount selector"""
        if not hasattr(self, 'mount_plan_selector'):
            return

        # ===== CRITICAL FIX: Defensive check for config_manager corruption =====
        if isinstance(self.config_manager, QComboBox):
            if LOGGING_AVAILABLE:
                logger.critical("CRITICAL: self.config_manager was corrupted (is QComboBox). Restoring...")
            from config_manager import ConfigManager
            self.config_manager = ConfigManager()
            # Try to restore profile selection if possible, otherwise list profiles might fail
        
        current_plan = self.mount_plan_selector.currentText()
        self.mount_plan_selector.clear()
        
        try:
            plans = self.config_manager.get_plans()
        except AttributeError:
             # Last resort fallback if restoration failed
            if LOGGING_AVAILABLE: logger.critical("Failed to restore config_manager.")
            plans = {}

        plan_names = list(plans.keys())
        self.mount_plan_selector.addItems(plan_names)
        
        # Restore selection or default
        try:
            active_plan = self.config_manager.get_active_plan()
        except:
            active_plan = None
        
        if current_plan and current_plan in plan_names:
            self.mount_plan_selector.setCurrentText(current_plan)
        elif active_plan and active_plan in plan_names:
            self.mount_plan_selector.setCurrentText(active_plan)
        elif plan_names:
            self.mount_plan_selector.setCurrentIndex(0)

    def open_mount_plan_editor(self):
        """Open the plan editor dialog from the mount tab"""
        dialog = PlanEditorDialog(self.config_manager, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_mount_plans()
            # Also update tools tab if it exists
            if hasattr(self, 'tools_tab'):
                self.tools_tab.load_plans()

    def mount_drive(self):
        if not self.profile_selector.currentText():
            QMessageBox.warning(self, self.tr("warning"), self.tr("select_profile_first"))
            return

        if self.bucket_selector.count() == 0:
            QMessageBox.warning(self, self.tr("warning"), self.tr("select_bucket_to_mount"))
            return

        drive_letter = self.drive_letter_input.currentText()
        profile_name = self.profile_selector.currentText()
        bucket_name = self.bucket_selector.currentText()
        
        # Obtener configuración del plan seleccionado
        plan_name = self.mount_plan_selector.currentText()
        plan_config = self.config_manager.get_plan(plan_name)

        # Mostrar mensaje inmediatamente en la barra de estado
        self.statusBar().showMessage(self.tr("status_mounting").format(bucket_name, drive_letter))
        description = f"mount_drive[{drive_letter}:{bucket_name}]"

        def execute_mount():
            success, message, process = self.rclone_manager.mount_drive(
                profile_name,
                drive_letter,
                bucket_name,
                plan_config=plan_config
            )
            return success, message, drive_letter, bucket_name, process

        def on_success(result):
            success, message, _letter, _bucket, process = result
            if success and self.multiple_mount_manager:
                try:
                    self.multiple_mount_manager.record_mount_success(_letter, profile_name, _bucket, process)
                except Exception as exc:
                    if LOGGING_AVAILABLE:
                        logger.warning("No se pudo registrar montaje múltiple: %s", exc, exc_info=True)
            if LOGGING_AVAILABLE:
                logger.info("Montaje completado (%s): %s", description, message)
            self._handle_mount_result(success, message, _letter, _bucket, process)

        def on_error(exc):
            error_msg = f"Error inesperado: {exc}"
            if LOGGING_AVAILABLE:
                logger.error("Error en tarea de montaje (%s): %s", description, str(exc), exc_info=True)
            self._handle_mount_result(False, error_msg, drive_letter, bucket_name, None)

        self.task_runner.run(
            execute_mount,
            on_success=on_success,
            on_error=on_error,
            description=description,
        )
    
    def _handle_mount_result(self, success, message, drive_letter, bucket_name, process=None):
        """Manejar resultado del montaje desde señal (thread-safe)"""
        if success:
            self._on_mount_success(drive_letter, bucket_name, message, process)
        else:
            self._on_mount_error(message)
        self._refresh_multi_mounts_widget()
    
    def _on_mount_success(self, drive_letter, bucket_name, message, process=None):
        """Manejar éxito del montaje"""
        try:
            self.mount_status_label.setText(self.tr("status_mounted").format(drive_letter))
            self.mount_button.setEnabled(False)
            self.unmount_button.setEnabled(True)
            self.open_drive_button.setEnabled(True)
            self.statusBar().showMessage(self.tr("status_mount_success").format(drive_letter), 5000)
            
            # ===== AUDITORÍA =====
            if self.audit_logger:
                self.audit_logger.log(
                    AuditEventType.DRIVE_MOUNTED,
                    {'drive_letter': drive_letter, 'bucket_name': bucket_name},
                    success=True
                )
            
            # ===== ACTUALIZAR MONITOR =====
            if self.state_monitor:
                self.state_monitor.update_component_status(
                    'rclone_manager',
                    ComponentStatus.RUNNING,
                    {'mounted_drives': [drive_letter]}
                )
            
            # ===== NOTIFICACIÓN DE ÉXITO =====
            if self.notification_manager:
                self.notification_manager.notify_mount_success(drive_letter, bucket_name)
            
            # Actualizar tooltip de bandeja
            self._update_tray_tooltip()

            # ✅ Refrescar la detección después de 3 segundos para mostrar la nueva unidad
            QTimer.singleShot(3000, self.detect_mounted_drives)
            
            # Mostrar el botón de cerrar sin desmontar
            self.update_close_without_unmount_button_visibility()
        except Exception as e:
            if LOGGING_AVAILABLE:
                logger.error(f"Error al procesar éxito de montaje: {e}")
    
    def _on_mount_error(self, error_msg):
        """Manejar error del montaje"""
        try:
            needs_winfsp = "winfsp" in error_msg.lower()
            
            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Icon.Critical)
            msg_box.setWindowTitle(self.tr("mount_error_title"))
            msg_box.setText(self.tr("mount_error_text"))
            msg_box.setInformativeText(error_msg)
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
            
            install_button = None
            if needs_winfsp and self.install_winfsp_callback:
                install_button = msg_box.addButton(self.tr("install_winfsp_button"), QMessageBox.ButtonRole.ActionRole)

            msg_box.exec()

            self.statusBar().showMessage(self.tr("status_mount_error"), 5000)

            if install_button and msg_box.clickedButton() == install_button:
                self.statusBar().showMessage(self.tr("status_installing_winfsp"))
                self.install_winfsp_callback()
        except Exception as e:
            if LOGGING_AVAILABLE:
                logger.error(f"Error al procesar error de montaje: {e}")
            self.open_drive_button.setEnabled(False)

    def set_winfsp_installer(self, callback):
        """Registrar callback para instalar WinFsp desde la UI"""
        self.install_winfsp_callback = callback

    def open_drive(self):
        """Abrir la unidad montada en el Explorador de archivos"""
        drive_letter = self.drive_letter_input.currentText()
        if not drive_letter:
            return

        path = f"{drive_letter}:\\"
        if not os.path.exists(path):
            QMessageBox.warning(self, self.tr("warning"), self.tr("drive_not_ready").format(drive_letter))
            self.open_drive_button.setEnabled(False)
            return

        try:
            os.startfile(path)
        except Exception as ex:
            QMessageBox.critical(self, self.tr("error"), self.tr("drive_open_failed").format(drive_letter, str(ex)))

    def unmount_drive(self):
        """Desmonta la unidad seleccionada usando la misma lógica del botón naranja"""
        drive_letter = self.drive_letter_input.currentText()

        if not drive_letter:
            QMessageBox.warning(
                self,
                self.tr("select_drive_letter_title"),
                self.tr("select_drive_letter_text")
            )
            return

        self.unmount_specific_drive(drive_letter)

    def update_unmount_button_state(self, *args, detected_drives=None):
        """Actualizar el estado de los botones de acuerdo con la letra seleccionada"""
        selected_letter = self.drive_letter_input.currentText()

        if not selected_letter:
            self.unmount_button.setEnabled(False)
            self.open_drive_button.setEnabled(False)
            self.mount_button.setEnabled(False)
            self.mount_status_label.setText("⭕ Selecciona una letra de unidad")
            return

        mounted_letters = []

        if detected_drives is not None:
            mounted_letters = [d['letter'] for d in detected_drives] if detected_drives else []
        else:
            try:
                detected = DriveDetector.detect_mounted_drives()
                mounted_letters = [d['letter'] for d in detected] if detected else []
            except Exception as e:
                print(f"Error detectando unidades: {e}")

        is_mounted = selected_letter in mounted_letters

        if is_mounted:
            self.unmount_button.setEnabled(True)
            self.unmount_button.setStyleSheet("background-color: #2196F3; color: white; font-weight: bold; border-radius: 5px; padding: 8px;")
            self.open_drive_button.setEnabled(True)
            self.mount_button.setEnabled(False)
            self.mount_button.setStyleSheet("background-color: #CCCCCC; color: gray; font-weight: bold; border-radius: 5px; padding: 8px;")
            self.mount_status_label.setText(self.tr("drive_letter_mounted_status").format(selected_letter))
        else:
            self.unmount_button.setEnabled(False)
            self.unmount_button.setStyleSheet("background-color: #CCCCCC; color: gray; font-weight: bold; border-radius: 5px; padding: 8px;")
            self.open_drive_button.setEnabled(False)
            self.mount_button.setEnabled(True)
            self.mount_button.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; border-radius: 5px; padding: 8px;")
            self.mount_status_label.setText(self.tr("drive_letter_not_mounted_status").format(selected_letter))

    def format_bucket(self):
        if not self.s3_handler:
            QMessageBox.warning(self, self.tr("warning"), self.tr("select_profile_first"))
            return

        if self.bucket_selector.count() == 0:
            QMessageBox.warning(self, self.tr("warning"), self.tr("no_buckets_available"))
            return

        bucket_name = self.bucket_selector.currentText()

        reply = QMessageBox.question(
            self, 
            self.tr("format_bucket_confirm_title"), 
            self.tr("format_bucket_confirm_text").format(bucket_name),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            # Double confirmation
            confirm_text, ok = QMessageBox.getText(
                self,
                self.tr("format_bucket_final_confirm_title"),
                self.tr("format_bucket_final_confirm_text").format(bucket_name)
            )

            if ok and confirm_text == bucket_name:
                self.statusBar().showMessage(self.tr("formatting_bucket_status").format(bucket_name))
                success = self.s3_handler.delete_all_objects(bucket_name)
                
                if success:
                    QMessageBox.information(self, self.tr("success"), self.tr("bucket_formatted_message").format(bucket_name))
                    self.statusBar().showMessage(self.tr("bucket_formatted"), 5000)
                else:
                    QMessageBox.critical(self, self.tr("error"), self.tr("format_failed"))
                    self.statusBar().showMessage(self.tr("format_failed"), 5000)
            else:
                self.statusBar().showMessage(self.tr("format_cancelled"), 3000)

    def open_settings(self):
        self.settings_window = SettingsWindow(self.config_manager, self)
        self.settings_window.profiles_updated.connect(self.update_profiles)
        self.settings_window.show()

    def update_profiles(self):
        current_profile = self.profile_selector.currentText()
        self.profile_selector.clear()
        profiles = self.config_manager.list_profiles()
        self.profile_selector.addItems(profiles)
        if current_profile in profiles:
            self.profile_selector.setCurrentText(current_profile)
        elif profiles:
            self.load_profile(profiles[0])
        else:
            self.load_profile(None)
    
    def update_close_without_unmount_button_visibility(self):
        """Actualiza la visibilidad del botón 'Cerrar sin Desmontar' basado en unidades montadas"""
        try:
            # from drive_detector import DriveDetector (Eliminado)
            detected_drives = DriveDetector.detect_mounted_drives()
            
            if detected_drives and len(detected_drives) > 0:
                # Hay unidades montadas, mostrar el botón
                self.close_without_unmount_button.show()
            else:
                # No hay unidades montadas, ocultar el botón
                self.close_without_unmount_button.hide()
        except Exception as e:
            # Si hay error, ocultar el botón por seguridad
            self.close_without_unmount_button.hide()
            if LOGGING_AVAILABLE:
                logger.warning(f"Error al actualizar visibilidad del botón: {e}")
    
    def detect_mounted_drives(self):
        """Detecta todas las unidades montadas por rclone"""
        self.drives_list.setPlainText("🔍 Detectando unidades montadas...\n")
        self.drives_list.repaint()
        
        detected_drives = []  # ✅ Inicializar FUERA del try para que esté disponible después
        
        try:
            detected_drives = DriveDetector.detect_mounted_drives()
            
            # Actualizar visibilidad del botón
            self.update_close_without_unmount_button_visibility()
            
            if not detected_drives:
                self.drives_list.setPlainText(
                    "ℹ️ No se detectaron unidades montadas\n\n"
                    "No hay unidades V:, W:, X:, Y:, Z: montadas actualmente.\n"
                    "Todas las letras están disponibles para montar."
                )
                self.unmount_all_btn.setEnabled(False)
                self.open_drive_button.setEnabled(False)
                
                # OCULTAR el contenedor de botones individuales
                if hasattr(self, 'individual_buttons_container'):
                    self.individual_buttons_container.hide()
                
                # Limpiar botones individuales si existen
                if hasattr(self, 'individual_unmount_buttons'):
                    for btn in self.individual_unmount_buttons:
                        btn.setParent(None)
                        btn.deleteLater()
                    self.individual_unmount_buttons = []
            else:
                result_text = f"✅ Se detectaron {len(detected_drives)} unidad(es) montada(s):\n\n"
                
                for drive in detected_drives:
                    result_text += f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    result_text += f"💿 Unidad: {drive['letter']}:\n"
                    result_text += f"📁 Ruta: {drive['path']}\n"
                    result_text += f"🏷️  Etiqueta: {drive['label']}\n"
                    
                    if drive['has_process']:
                        result_text += f"🔧 Proceso(s): {drive['process_ids']}\n"
                        result_text += f"✅ Estado: Proceso activo\n\n"
                    else:
                        result_text += f"⚠️  Proceso: No detectado (sesión anterior)\n"
                        result_text += f"📌 Estado: Montada sin proceso activo\n\n"
                
                result_text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                result_text += "\n💡 Usa los botones individuales o 'Desmontar Todas'."
                
                self.drives_list.setPlainText(result_text)
                self.unmount_all_btn.setEnabled(True)
                
                # MOSTRAR el contenedor de botones individuales
                if hasattr(self, 'individual_buttons_container'):
                    self.individual_buttons_container.show()
                
                # Crear botones individuales de desmontaje
                self.create_individual_unmount_buttons(detected_drives)
                
                # Actualizar status bar
                self.statusBar().showMessage(
                    f"✅ {len(detected_drives)} unidad(es) detectada(s): " + 
                    ", ".join([d['letter'] + ":" for d in detected_drives]),
                    5000
                )
        
        except Exception as e:
            error_msg = f"❌ Error al detectar unidades:\n\n{str(e)}\n\n"
            error_msg += "Asegúrate de que tienes los permisos necesarios."
            self.drives_list.setPlainText(error_msg)
            self.unmount_all_btn.setEnabled(False)
            detected_drives = []
            
            QMessageBox.critical(
                self,
                "Error de Detección",
                f"No se pudieron detectar las unidades montadas:\n\n{str(e)}"
            )
        finally:
            self.update_unmount_button_state(detected_drives=detected_drives)
            self._refresh_multi_mounts_widget()
    
    def create_individual_unmount_buttons(self, detected_drives):
        """Crea botones individuales para desmontar cada unidad"""
        # Limpiar layout existente
        while self.individual_buttons_container_layout.count():
            item = self.individual_buttons_container_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        if not detected_drives:
            # Si no hay unidades, ocultar el contenedor
            self.individual_buttons_container.hide()
            return
        
        # Etiqueta de sección
        label = QLabel("🎯 Desmontar Unidades Específicas:")
        label.setStyleSheet("font-weight: bold; color: #3498db; margin-top: 10px;")
        self.individual_buttons_container_layout.addWidget(label)
        
        # Crear un botón para cada unidad
        for drive in detected_drives:
            btn_layout = QHBoxLayout()
            
            # Botón de desmontaje
            unmount_btn = QPushButton(f"🗑️ Desmontar {drive['letter']}:")
            unmount_btn.clicked.connect(lambda checked, letter=drive['letter']: self.unmount_specific_drive(letter))
            unmount_btn.setStyleSheet("""
                QPushButton {
                    background-color: #e67e22;
                    color: white;
                    border: none;
                    padding: 8px 15px;
                    font-size: 10pt;
                    font-weight: bold;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #d35400;
                }
            """)
            
            # Etiqueta con info
            info_label = QLabel(f"({drive['label'][:30]}{'...' if len(drive['label']) > 30 else ''})")
            info_label.setStyleSheet("color: #95a5a6; font-size: 9pt;")
            
            btn_layout.addWidget(unmount_btn)
            btn_layout.addWidget(info_label)
            btn_layout.addStretch()
            
            self.individual_buttons_container_layout.addLayout(btn_layout)
        
        # Mostrar el contenedor
        self.individual_buttons_container.show()
    
    def unmount_specific_drive(self, drive_letter: str):
        """Desmonta una unidad específica"""
        reply = QMessageBox.question(
            self,
            "⚠️ Confirmar Desmontaje",
            f"¿Estás seguro de que deseas desmontar la unidad {drive_letter}:?\n\n"
            f"Los archivos abiertos desde esta unidad se cerrarán.\n"
            f"Las demás unidades permanecerán montadas.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.statusBar().showMessage(self.tr("status_unmounting_drive").format(drive_letter))
            
            try:
                if self.multiple_mount_manager:
                    success, message = self.multiple_mount_manager.unmount_drive(drive_letter)
                    if not success:
                        # Fallback a detección manual
                        success, message = DriveDetector.unmount_drive(drive_letter, self.translations)
                else:
                    success, message = DriveDetector.unmount_drive(drive_letter, self.translations)
                
                if success:
                    self.statusBar().showMessage(self.tr("status_unmount_drive_success").format(message), 3000)
                    
                    # Actualizar visibilidad del botón después de desmontar
                    QTimer.singleShot(1000, self.update_close_without_unmount_button_visibility)
                    
                    # ===== AUDITORÍA =====
                    if self.audit_logger:
                        self.audit_logger.log(
                            AuditEventType.DRIVE_UNMOUNTED,
                            {'drive_letter': drive_letter},
                            success=True
                        )
                    
                    # ===== ACTUALIZAR MONITOR =====
                    if self.state_monitor:
                        # Obtener lista actualizada de unidades montadas
                        # from drive_detector import DriveDetector (Eliminado: Import global ya existe)
                        mounted = DriveDetector.detect_mounted_drives()
                        mounted_letters = [d['letter'] for d in mounted] if mounted else []
                        if not mounted_letters:
                            self.state_monitor.update_component_status(
                                'rclone_manager',
                                ComponentStatus.READY,
                                {'mounted_drives': []}
                            )
                    
                    # ===== NOTIFICACIÓN DE DESMONTAJE =====
                    if self.notification_manager:
                        self.notification_manager.notify_unmount_success(drive_letter)
                    
                    # Actualizar tooltip de bandeja
                    self._update_tray_tooltip()
                    
                    # Función para actualizar la UI completamente
                    def refresh_ui_complete():
                        # 1. Refrescar la detección de unidades montadas
                        self.detect_mounted_drives()
                        
                        # 2. Rehabilitar el botón "Montar como Unidad"
                        self.mount_button.setEnabled(True)
                        
                        # 3. Deshabilitar el botón "Desmontar Unidad"
                        self.unmount_button.setEnabled(False)

                        # 3b. Deshabilitar botón de abrir hasta que vuelva a montarse
                        self.open_drive_button.setEnabled(False)
                        
                        # 4. Actualizar el estado del montaje
                        self.mount_status_label.setText(self.tr("status_not_mounted"))
                    
                    # Esperar 2 segundos para asegurar que la unidad se libere completamente
                    QTimer.singleShot(2000, refresh_ui_complete)
                    self._refresh_multi_mounts_widget()
                else:
                    QMessageBox.critical(
                        self,
                        self.tr("error"),
                        self.tr("error_unmount_drive").format(drive_letter, message)
                    )
                    self.statusBar().showMessage(self.tr("status_unmount_drive_error").format(drive_letter), 5000)
                    self._refresh_multi_mounts_widget()
                    
            except Exception as e:
                QMessageBox.critical(
                    self,
                    self.tr("error"),
                    self.tr("error_unexpected_unmount_drive").format(drive_letter, str(e))
                )
                self._refresh_multi_mounts_widget()
    
    def unmount_all_detected_drives(self):
        """Desmonta todas las unidades detectadas (Asíncrono)"""
        reply = QMessageBox.question(
            self,
            self.tr("confirm_unmount_all_title"),
            self.tr("confirm_unmount_all_text"),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.statusBar().showMessage(self.tr("status_unmounting_all"))
            self.unmount_all_btn.setEnabled(False) # Deshabilitar inmediatamente
            
            description = "unmount_all_drives"

            def execute_unmount():
                success = False
                message = ""
                if self.multiple_mount_manager:
                    success, message = self.multiple_mount_manager.unmount_all()
                    if not success:
                        # Intentar fallback para cualquier unidad residual
                        # Nota: DriveDetector.unmount_all_drives puede ser bloqueante
                        from drive_detector import DriveDetector
                        success_fallback, message_fallback = DriveDetector.unmount_all_drives(self.translations)
                        if success_fallback:
                            success = True
                            message = message_fallback
                else:
                    from drive_detector import DriveDetector
                    success, message = DriveDetector.unmount_all_drives(self.translations)
                return success, message

            def on_success(result):
                success, message = result
                
                # Actualizar visibilidad del botón después de desmontar todas
                QTimer.singleShot(1000, self.update_close_without_unmount_button_visibility)
                
                if success:
                    self.drives_list.setPlainText(self.tr("unmount_all_success_details").format(message))
                    self.unmount_all_btn.setEnabled(False)
                    
                    # También actualizar el estado del botón de unmount principal
                    self.unmount_button.setEnabled(False)
                    self.open_drive_button.setEnabled(False)
                    self.mount_button.setEnabled(True)
                    self.mount_status_label.setText(self.tr("status_not_mounted"))
                    
                    # Ocultar el contenedor de botones individuales
                    if hasattr(self, 'individual_buttons_container'):
                        self.individual_buttons_container.hide()
                    
                    QMessageBox.information(
                        self,
                        self.tr("success"),
                        message
                    )
                    
                    self.statusBar().showMessage(self.tr("status_unmount_all_success").format(message), 5000)
                    self._refresh_multi_mounts_widget()
                else:
                    self.drives_list.setPlainText(self.tr("unmount_all_error_details").format(message))
                    self.unmount_all_btn.setEnabled(True) # Rehabilitar si falló
                    QMessageBox.critical(
                        self,
                        self.tr("error"),
                        self.tr("error_unmount_all").format(message)
                    )
                    self.statusBar().showMessage(self.tr("status_unmount_all_error"), 5000)
                    self._refresh_multi_mounts_widget()

            def on_error(exc):
                self.unmount_all_btn.setEnabled(True) # Rehabilitar si hubo error
                error_msg = str(dict(exc) if hasattr(exc, '__dict__') else str(exc))
                self.drives_list.setPlainText(self.tr("unmount_all_unexpected_error_details").format(error_msg))
                QMessageBox.critical(
                    self,
                    self.tr("error"),
                    self.tr("error_unexpected_unmount_all").format(error_msg)
                )
                if LOGGING_AVAILABLE:
                    logger.error(f"Error inesperado en unmount_all: {exc}", exc_info=True)
                self._refresh_multi_mounts_widget()

            self.task_runner.run(
                execute_unmount,
                on_success=on_success,
                on_error=on_error,
                description=description
            )

    def closeEvent(self, event):
        """Gestionar el cierre de la aplicación con opción de segundo plano"""
        if self._force_quit or not self._should_keep_in_background():
            self._execute_shutdown_tasks()
            event.accept()
            return

        # Si hay icono en bandeja, minimizar a bandeja en lugar de cerrar
        if self.tray_icon and self.tray_icon.isVisible():
            event.ignore()
            self.hide()
            
            # Notificar la primera vez
            if not self._tray_notified and self.notification_manager:
                self.notification_manager.info(
                    self.tr("app_name"),
                    self.tr("tray_running_notification")
                )
                self._tray_notified = True
            return

        # Si no hay bandeja, mostrar diálogo
        dialog = QMessageBox(self)
        dialog.setIcon(QMessageBox.Icon.Information)
        dialog.setWindowTitle(self.tr("background_running_title"))
        dialog.setText(self.tr("background_running_message"))
        keep_btn = dialog.addButton(self.tr("background_keep_running"), QMessageBox.ButtonRole.AcceptRole)
        exit_btn = dialog.addButton(self.tr("background_exit"), QMessageBox.ButtonRole.DestructiveRole)
        cancel_btn = dialog.addButton(QMessageBox.StandardButton.Cancel)

        dialog.exec()

        clicked = dialog.clickedButton()
        if clicked == keep_btn:
            event.ignore()
            self.send_to_tray(show_message=True)
        elif clicked == exit_btn:
            self._force_quit = True
            self._execute_shutdown_tasks()
            event.accept()
        else:
            event.ignore()
    
    def _on_scheduled_task_executed(self, task_id: str, success: bool, message: str):
        """Manejar ejecución de tarea programada"""
        if LOGGING_AVAILABLE:
            logger.info(f"Tarea programada ejecutada: {task_id} - {message}")
        if self.audit_logger:
            self.audit_logger.log(
                AuditEventType.SYNC_STARTED if 'sync' in task_id.lower() else AuditEventType.BACKUP_STARTED,
                {'task_id': task_id, 'message': message},
                success=success
            )
    
    def _on_scheduled_task_error(self, task_id: str, error_message: str):
        """Manejar error en tarea programada"""
        if LOGGING_AVAILABLE:
            logger.error(f"Error en tarea programada {task_id}: {error_message}")
        if self.audit_logger:
            self.audit_logger.log(
                AuditEventType.ERROR_OCCURRED,
                {'task_id': task_id},
                success=False,
                error_message=error_message
            )
    
    def update_dashboard_stats(self, force_remote=False):
        """Actualizar estadísticas del dashboard (Mejora #52)"""
        if not hasattr(self, 'dashboard_tab'):
            return

        try:
            from datetime import datetime
            stats = {}

            # Obtener espacio usado del bucket
            if self.s3_handler and self.bucket_selector.count() > 0:
                try:
                    bucket_name = self.bucket_selector.currentText()
                    # Obtener tamaño real del bucket
                    space_used, error_msg = self.s3_handler.get_bucket_size(bucket_name, use_cache=not force_remote)

                    if error_msg:
                        if LOGGING_AVAILABLE:
                            logger.warning(f"Error al obtener tamaño del bucket: {error_msg}")
                        stats['space_used'] = 0
                        stats['space_total'] = 0
                    else:
                        stats['space_used'] = space_used if space_used else 0
                        # Vultr Object Storage: Los planes típicos son:
                        # - Starter: 250 GB
                        # - Performance: 1 TB (1024 GB)
                        # - Enterprise: Ilimitado
                        # Por defecto usamos 1 TB, pero el usuario puede tener más
                        # Si el espacio usado es mayor a 1 TB, ajustamos el total
                        if space_used > 1024 * 1024 * 1024 * 1024:  # Si usa más de 1 TB
                            # Estimar que tiene al menos 2x lo usado, o usar 10 TB como máximo razonable
                            estimated_total = max(space_used * 2, 10 * 1024 * 1024 * 1024 * 1024)
                            stats['space_total'] = estimated_total
                        else:
                            # Usar 1 TB como referencia estándar
                            stats['space_total'] = 1024 * 1024 * 1024 * 1024  # 1 TB en bytes
                except Exception as e:
                    if LOGGING_AVAILABLE:
                        logger.error(f"Error al obtener estadísticas del bucket: {e}")
                    stats['space_used'] = 0
                    stats['space_total'] = 0
            else:
                stats['space_used'] = 0
                stats['space_total'] = 0
            
            # Obtener archivos sincronizados hoy
            stats['files_synced_today'] = 0  # TODO: Implementar contador
            
            # Velocidad de transferencia
            stats['transfer_speed'] = 0.0  # TODO: Implementar
            
            # Última sincronización
            if self.real_time_sync and self.real_time_sync.is_running():
                stats['last_sync'] = datetime.now()
            else:
                stats['last_sync'] = None
            
            # Unidades montadas
            try:
                # from drive_detector import DriveDetector (Eliminado)
                detected = DriveDetector.detect_mounted_drives()
                stats['mounted_drives'] = [d['letter'] for d in detected] if detected else []
            except:
                stats['mounted_drives'] = []
            
            # Actualizar dashboard
            self.dashboard_tab.update_stats(stats)
        except Exception as e:
            if ERROR_HANDLING_AVAILABLE:
                error = handle_error(e, context="update_dashboard_stats")
                if self.notification_manager:
                    self.notification_manager.warning("Dashboard", f"Error al actualizar: {error.message}")
            if LOGGING_AVAILABLE:
                logger.error(f"Error al actualizar dashboard: {e}", exc_info=True)
    
    # ===== NUEVO: Gestión de Buckets desde GUI =====
    
    def create_bucket(self):
        """Crear nuevo bucket mediante diálogo"""
        if not self.s3_handler:
            QMessageBox.warning(self, "Advertencia", "Selecciona un perfil primero")
            return
        
        # Importar diálogo
        try:
            from ui.bucket_dialog import BucketDialog
        except ImportError as e:
            QMessageBox.critical(self, "Error", f"No se pudo cargar el diálogo: {e}")
            return
        
        # Mostrar diálogo
        dialog = BucketDialog(self, self.translations)
        
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        
        bucket_name = dialog.get_bucket_name()
        
        if not bucket_name:
            return
        
        # Ejecutar creación en background
        self.statusBar().showMessage(f"Creando bucket '{bucket_name}'...")
        self.create_bucket_btn.setEnabled(False)  # Deshabilitar botón
        
        description = f"create_bucket[{bucket_name}]"
        
        def execute_create():
            return self.s3_handler.create_bucket(bucket_name)
        
        def on_success(result):
            success, message = result
            
            if success:
                QMessageBox.information(self, "✅ Éxito", message)
                # Refrescar lista de buckets
                self.refresh_buckets(force_remote=True)
                self.statusBar().showMessage(message, 5000)
            else:
                QMessageBox.critical(self, "❌ Error", message)
                self.statusBar().showMessage(f"Error: {message}", 5000)
            
            self.create_bucket_btn.setEnabled(True)
        
        def on_error(exc):
            error_msg = f"Error inesperado: {str(exc)}"
            QMessageBox.critical(self, "❌ Error", error_msg)
            self.statusBar().showMessage(error_msg, 5000)
            self.create_bucket_btn.setEnabled(True)
            if LOGGING_AVAILABLE:
                logger.error(f"Error al crear bucket: {exc}", exc_info=True)
        
        self.task_runner.run(
            execute_create,
            on_success=on_success,
            on_error=on_error,
            description=description
        )
    
    def delete_bucket(self):
        """Eliminar bucket seleccionado con confirmación doble"""
        bucket_name = self.bucket_selector.currentText()
        
        if not bucket_name:
            QMessageBox.warning(self, "Advertencia", "Selecciona un bucket primero")
            return
        
        if not self.s3_handler:
            QMessageBox.warning(self, "Advertencia", "No hay perfil activo")
            return
        
        # Confirmación 1: Diálogo estándar
        reply = QMessageBox.question(
            self,
            "⚠️ Confirmar Eliminación",
            f"¿Estás seguro de que deseas eliminar el bucket '{bucket_name}'?\n\n"
            f"⚠️ Esta acción es IRREVERSIBLE.\n"
            f"⚠️ Todos los archivos del bucket serán eliminados.\n\n"
            f"¿Deseas continuar?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            self.statusBar().showMessage("Eliminación cancelada", 3000)
            return
        
        # Confirmación 2: Escribir nombre del bucket
        from PyQt6.QtWidgets import QInputDialog
        text, ok = QInputDialog.getText(
            self,
            "🔒 Confirmación Final",
            f"Escribe el nombre del bucket para confirmar:\n\n{bucket_name}"
        )
        
        if not ok or text != bucket_name:
            self.statusBar().showMessage("Eliminación cancelada (nombre no coincide)", 3000)
            return
        
        # Ejecutar eliminación en background
        self.statusBar().showMessage(f"Eliminando bucket '{bucket_name}'...")
        self.delete_bucket_btn.setEnabled(False)
        
        description = f"delete_bucket[{bucket_name}]"
        
        def execute_delete():
            # force=True para eliminar incluso con contenido
            return self.s3_handler.delete_bucket(bucket_name, force=True)
        
        def on_success(result):
            success, message = result
            
            if success:
                QMessageBox.information(self, "✅ Éxito", message)
                # Refrescar lista de buckets
                self.refresh_buckets(force_remote=True)
                self.statusBar().showMessage(message, 5000)
            else:
                QMessageBox.critical(self, "❌ Error", message)
                self.statusBar().showMessage(f"Error: {message}", 5000)
            
            self.delete_bucket_btn.setEnabled(bool(self.bucket_selector.currentText()))
        
        def on_error(exc):
            error_msg = f"Error inesperado: {str(exc)}"
            QMessageBox.critical(self, "❌ Error", error_msg)
            self.statusBar().showMessage(error_msg, 5000)
            self.delete_bucket_btn.setEnabled(bool(self.bucket_selector.currentText()))
            if LOGGING_AVAILABLE:
                logger.error(f"Error al eliminar bucket: {exc}", exc_info=True)
        
        self.task_runner.run(
            execute_delete,
            on_success=on_success,
            on_error=on_error,
            description=description
        )


