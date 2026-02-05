"""
Main Window v2 - Nueva ventana principal con arquitectura de barra lateral

Esta versión reemplaza la estructura de pestañas planas con una barra lateral
que agrupa los tipos de almacenamiento.
"""

import sys
import os

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QApplication, QPushButton, QLabel, QSystemTrayIcon,
    QMenu, QMessageBox, QComboBox
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QIcon, QFont, QAction

# Managers
from config_manager import ConfigManager
from rclone_manager import RcloneManager

# UI Components
from ui.sidebar import Sidebar
from ui.content_panel import ContentPanel
from ui.storage_types import VultrS3Storage, MegaStorage

# Translations
try:
    from translations import tr
    TRANSLATIONS_AVAILABLE = True
except ImportError:
    TRANSLATIONS_AVAILABLE = False
    def tr(key): return key


class MainWindowV2(QMainWindow):
    """
    Nueva ventana principal con arquitectura de barra lateral.
    
    La interfaz está dividida en:
    - Barra lateral izquierda: Tipos de almacenamiento
    - Panel derecho: Contenido contextual según el tipo seleccionado
    """
    
    def __init__(self):
        super().__init__()
        
        # Managers
        self.config_manager = ConfigManager()
        self.rclone_manager = RcloneManager(self.config_manager)
        
        # Storage handlers registry
        self.storage_handlers = {}
        
        # Initialize UI
        self.init_ui()
        self.register_storage_types()
        self.setup_tray()
        
    def init_ui(self):
        """Inicializa la interfaz principal"""
        self.setWindowTitle("VultrDrive Desktop")
        self.setMinimumSize(1100, 700)
        
        # Estilo global oscuro
        self.setStyleSheet("""
            QMainWindow {
                background-color: #0f0f1a;
            }
            QWidget {
                color: #ecf0f1;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QGroupBox {
                border: 1px solid #34495e;
                border-radius: 8px;
                margin-top: 15px;
                padding: 15px;
                font-weight: bold;
                background-color: #1a1a2e;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 10px;
                color: #3498db;
            }
            QLineEdit, QComboBox {
                background-color: #2c3e50;
                border: 1px solid #34495e;
                border-radius: 5px;
                padding: 8px 12px;
                color: white;
            }
            QLineEdit:focus, QComboBox:focus {
                border-color: #3498db;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 8px solid #bdc3c7;
                margin-right: 10px;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #2573a7;
            }
            QPushButton:disabled {
                background-color: #7f8c8d;
                color: #bdc3c7;
            }
            QListWidget {
                background-color: #1a1a2e;
                border: 1px solid #34495e;
                border-radius: 5px;
                padding: 5px;
            }
            QListWidget::item {
                padding: 8px;
                border-radius: 3px;
            }
            QListWidget::item:selected {
                background-color: #3498db;
            }
            QListWidget::item:hover:!selected {
                background-color: #2c3e50;
            }
            QProgressBar {
                border: none;
                border-radius: 5px;
                background-color: #34495e;
                height: 8px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #27ae60;
                border-radius: 5px;
            }
            QScrollBar:vertical {
                background-color: #1a1a2e;
                width: 10px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background-color: #34495e;
                border-radius: 5px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #4a6278;
            }
        """)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal horizontal
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Barra lateral
        self.sidebar = Sidebar()
        self.sidebar.storage_selected.connect(self.on_storage_selected)
        self.sidebar.add_storage_clicked.connect(self.on_add_storage_clicked)
        main_layout.addWidget(self.sidebar)
        
        # Panel de contenido
        self.content_panel = ContentPanel()
        main_layout.addWidget(self.content_panel, 1)
        
        # Barra de herramientas superior
        self.setup_toolbar()
    
    def setup_toolbar(self):
        """Configura la barra de herramientas superior"""
        toolbar = self.addToolBar("Herramientas")
        toolbar.setMovable(False)
        toolbar.setStyleSheet("""
            QToolBar {
                background-color: #1a1a2e;
                border-bottom: 1px solid #34495e;
                padding: 5px;
                spacing: 10px;
            }
        """)
        
        # Spacer
        spacer = QWidget()
        spacer.setSizePolicy(spacer.sizePolicy().Policy.Expanding, 
                            spacer.sizePolicy().Policy.Preferred)
        toolbar.addWidget(spacer)
        
        # Selector de idioma
        lang_label = QLabel("🌐")
        toolbar.addWidget(lang_label)
        
        self.lang_selector = QComboBox()
        self.lang_selector.addItems(["Español", "English", "Français", "Deutsch", "Português"])
        self.lang_selector.setMaximumWidth(120)
        toolbar.addWidget(self.lang_selector)
        
        # Botón de tema
        self.theme_btn = QPushButton("🌙")
        self.theme_btn.setMaximumWidth(40)
        self.theme_btn.setToolTip("Cambiar tema")
        toolbar.addWidget(self.theme_btn)
        
        # Botón de minimizar a bandeja
        self.minimize_btn = QPushButton("⬇️ Segundo Plano")
        self.minimize_btn.clicked.connect(self.minimize_to_tray)
        toolbar.addWidget(self.minimize_btn)
    
    def register_storage_types(self):
        """Registra los tipos de almacenamiento disponibles"""
        # Vultr S3
        vultr = VultrS3Storage(self.config_manager, self.rclone_manager)
        self.storage_handlers['vultr_s3'] = vultr
        self.sidebar.add_storage_type('vultr_s3', vultr.icon, vultr.name, vultr.color)
        
        # MEGA
        mega = MegaStorage(self.config_manager, self.rclone_manager)
        self.storage_handlers['mega'] = mega
        self.sidebar.add_storage_type('mega', mega.icon, mega.name, mega.color)
        
        # Placeholder para futuros tipos
        # self.sidebar.add_storage_type('gdrive', '📁', 'Google Drive', '#f4b400')
        # self.sidebar.add_storage_type('smb', '📂', 'Carpetas Compartidas', '#00897b')
    
    def on_storage_selected(self, storage_id: str):
        """Manejador cuando se selecciona un tipo de almacenamiento"""
        if storage_id in self.storage_handlers:
            handler = self.storage_handlers[storage_id]
            self.content_panel.set_storage_type(storage_id, handler)
    
    def on_add_storage_clicked(self):
        """Manejador cuando se hace clic en 'Agregar Nuevo'"""
        QMessageBox.information(
            self, 
            "Próximamente",
            "La posibilidad de agregar nuevos tipos de almacenamiento "
            "(Google Drive, OneDrive, Dropbox, etc.) estará disponible pronto.\n\n"
            "Por ahora puedes usar Vultr S3 y MEGA.nz."
        )
    
    def setup_tray(self):
        """Configura el icono de la bandeja del sistema"""
        self.tray_icon = QSystemTrayIcon(self)
        
        # Usar icono por defecto si no hay uno personalizado
        app = QApplication.instance()
        if app:
            self.tray_icon.setIcon(app.style().standardIcon(
                app.style().StandardPixmap.SP_ComputerIcon
            ))
        
        # Menú de la bandeja
        tray_menu = QMenu()
        
        show_action = QAction("Mostrar Ventana", self)
        show_action.triggered.connect(self.show_from_tray)
        tray_menu.addAction(show_action)
        
        tray_menu.addSeparator()
        
        exit_action = QAction("Salir", self)
        exit_action.triggered.connect(self.close_app)
        tray_menu.addAction(exit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.tray_activated)
    
    def minimize_to_tray(self):
        """Minimiza la aplicación a la bandeja del sistema"""
        self.hide()
        self.tray_icon.show()
        self.tray_icon.showMessage(
            "VultrDrive Desktop",
            "La aplicación sigue ejecutándose en segundo plano",
            QSystemTrayIcon.MessageIcon.Information,
            2000
        )
    
    def show_from_tray(self):
        """Muestra la ventana desde la bandeja"""
        self.show()
        self.activateWindow()
    
    def tray_activated(self, reason):
        """Manejador de activación del icono de bandeja"""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show_from_tray()
    
    def close_app(self):
        """Cierra la aplicación completamente"""
        self.tray_icon.hide()
        QApplication.quit()
    
    def closeEvent(self, event):
        """Manejador del evento de cierre"""
        reply = QMessageBox.question(
            self, 
            "Confirmar Cierre",
            "¿Deseas cerrar la aplicación?\n\n"
            "• 'Sí' = Cerrar completamente\n"
            "• 'No' = Minimizar a bandeja",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | 
            QMessageBox.StandardButton.Cancel
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.close_app()
        elif reply == QMessageBox.StandardButton.No:
            event.ignore()
            self.minimize_to_tray()
        else:
            event.ignore()


def main():
    """Punto de entrada de la aplicación"""
    app = QApplication(sys.argv)
    app.setApplicationName("VultrDrive Desktop")
    
    window = MainWindowV2()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
