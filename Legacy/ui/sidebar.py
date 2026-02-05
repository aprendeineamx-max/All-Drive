"""
Sidebar Widget - Barra lateral para selección de tipo de almacenamiento

Este widget muestra los diferentes tipos de almacenamiento disponibles
y permite al usuario seleccionar cuál configurar/usar.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QLabel, QFrame, QScrollArea, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont


class StorageTypeButton(QPushButton):
    """Botón personalizado para cada tipo de almacenamiento en la barra lateral"""
    
    def __init__(self, icon: str, name: str, color: str, storage_id: str, parent=None):
        super().__init__(parent)
        self.storage_id = storage_id
        self.color = color
        self._selected = False
        
        # Texto con icono
        self.setText(f"{icon} {name}")
        self.setFont(QFont("Segoe UI", 10))
        
        # Estilo base
        self.update_style()
        
        # Configuración
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(45)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
    
    def update_style(self):
        """Actualiza el estilo según si está seleccionado o no"""
        if self._selected:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {self.color};
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 10px 15px;
                    text-align: left;
                    font-weight: bold;
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    color: #bdc3c7;
                    border: none;
                    border-radius: 8px;
                    padding: 10px 15px;
                    text-align: left;
                }}
                QPushButton:hover {{
                    background-color: rgba(255, 255, 255, 0.1);
                    color: white;
                }}
            """)
    
    def set_selected(self, selected: bool):
        """Marca este botón como seleccionado o no"""
        self._selected = selected
        self.update_style()


class Sidebar(QWidget):
    """
    Barra lateral principal para navegación entre tipos de almacenamiento.
    
    Signals:
        storage_selected: Emitido cuando se selecciona un tipo de almacenamiento
                         Parámetro: storage_id (str)
        add_storage_clicked: Emitido cuando se hace clic en "Agregar Nuevo"
    """
    
    storage_selected = pyqtSignal(str)
    add_storage_clicked = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.storage_buttons = {}
        self._current_storage = None
        self.init_ui()
    
    def init_ui(self):
        """Inicializa la interfaz de la barra lateral"""
        self.setFixedWidth(220)
        self.setStyleSheet("""
            QWidget {
                background-color: #1a1a2e;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 15, 10, 15)
        layout.setSpacing(5)
        
        # Logo / Título
        title_label = QLabel("💾 VultrDrive")
        title_label.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title_label.setStyleSheet("color: white; padding: 10px 5px;")
        layout.addWidget(title_label)
        
        # Subtítulo
        subtitle = QLabel("Almacenamiento Universal")
        subtitle.setFont(QFont("Segoe UI", 9))
        subtitle.setStyleSheet("color: #7f8c8d; padding: 0 5px 15px 5px;")
        layout.addWidget(subtitle)
        
        # Separador
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("background-color: #2d3436;")
        separator.setFixedHeight(1)
        layout.addWidget(separator)
        
        # Etiqueta de sección
        section_label = QLabel("TIPOS DE ALMACENAMIENTO")
        section_label.setFont(QFont("Segoe UI", 8))
        section_label.setStyleSheet("color: #636e72; padding: 15px 5px 5px 5px;")
        layout.addWidget(section_label)
        
        # Contenedor scrollable para botones de almacenamiento
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("background-color: transparent;")
        
        self.buttons_container = QWidget()
        self.buttons_layout = QVBoxLayout(self.buttons_container)
        self.buttons_layout.setContentsMargins(0, 5, 0, 5)
        self.buttons_layout.setSpacing(3)
        
        scroll.setWidget(self.buttons_container)
        layout.addWidget(scroll, 1)
        
        # Separador antes de agregar
        separator2 = QFrame()
        separator2.setFrameShape(QFrame.Shape.HLine)
        separator2.setStyleSheet("background-color: #2d3436;")
        separator2.setFixedHeight(1)
        layout.addWidget(separator2)
        
        # Botón de agregar nuevo
        self.add_btn = QPushButton("➕ Agregar Nuevo")
        self.add_btn.setStyleSheet("""
            QPushButton {
                background-color: #00b894;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #00a381;
            }
        """)
        self.add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.add_btn.clicked.connect(self.add_storage_clicked.emit)
        layout.addWidget(self.add_btn)
    
    def add_storage_type(self, storage_id: str, icon: str, name: str, color: str):
        """
        Agrega un nuevo tipo de almacenamiento a la barra lateral.
        
        Args:
            storage_id: Identificador único del tipo
            icon: Emoji/icono para mostrar
            name: Nombre para mostrar
            color: Color hexadecimal para el botón activo
        """
        if storage_id in self.storage_buttons:
            return  # Ya existe
        
        btn = StorageTypeButton(icon, name, color, storage_id)
        btn.clicked.connect(lambda: self._on_storage_clicked(storage_id))
        
        self.storage_buttons[storage_id] = btn
        self.buttons_layout.addWidget(btn)
        
        # Si es el primero, seleccionarlo automáticamente
        if len(self.storage_buttons) == 1:
            self.select_storage(storage_id)
    
    def remove_storage_type(self, storage_id: str):
        """Elimina un tipo de almacenamiento de la barra lateral"""
        if storage_id in self.storage_buttons:
            btn = self.storage_buttons.pop(storage_id)
            self.buttons_layout.removeWidget(btn)
            btn.deleteLater()
            
            # Si era el seleccionado, seleccionar otro
            if self._current_storage == storage_id:
                if self.storage_buttons:
                    first_id = list(self.storage_buttons.keys())[0]
                    self.select_storage(first_id)
                else:
                    self._current_storage = None
    
    def select_storage(self, storage_id: str):
        """Selecciona un tipo de almacenamiento"""
        if storage_id not in self.storage_buttons:
            return
        
        # Deseleccionar el anterior
        if self._current_storage and self._current_storage in self.storage_buttons:
            self.storage_buttons[self._current_storage].set_selected(False)
        
        # Seleccionar el nuevo
        self._current_storage = storage_id
        self.storage_buttons[storage_id].set_selected(True)
        
        # Emitir señal
        self.storage_selected.emit(storage_id)
    
    def _on_storage_clicked(self, storage_id: str):
        """Manejador de clic en un botón de almacenamiento"""
        if storage_id != self._current_storage:
            self.select_storage(storage_id)
    
    def get_current_storage(self) -> str:
        """Retorna el ID del tipo de almacenamiento actualmente seleccionado"""
        return self._current_storage
    
    def clear_storage_types(self):
        """Elimina todos los tipos de almacenamiento de la barra"""
        for storage_id in list(self.storage_buttons.keys()):
            self.remove_storage_type(storage_id)
