"""
Progress Dialog - VultrDrive Desktop
Mejora #5: Barra de Progreso para Operaciones

Widget reutilizable para mostrar progreso de operaciones:
- Montaje de disco
- Sincronización
- Carga/descarga de archivos
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QProgressBar, QPushButton, QWidget)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont
import time

class ProgressDialog(QDialog):
    """
    Diálogo de progreso con información detallada
    
    Muestra:
    - Barra de progreso
    - Velocidad (MB/s)
    - Tiempo estimado restante
    - Archivos procesados / total
    - Mensaje de estado
    """
    
    # Señal para cancelar operación
    cancelled = pyqtSignal()
    
    def __init__(self, parent=None, title="Procesando...", can_cancel=True):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setMinimumWidth(400)
        self.setMinimumHeight(200)
        
        # Variables de estado
        self.start_time = None
        self.last_update_time = None
        self.last_bytes = 0
        self.current_speed = 0.0
        self.can_cancel = can_cancel
        
        self.setup_ui()
        
    def setup_ui(self):
        """Configurar la interfaz del diálogo"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Mensaje de estado
        self.status_label = QLabel("Iniciando...")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        status_font = QFont()
        status_font.setPointSize(10)
        status_font.setBold(True)
        self.status_label.setFont(status_font)
        layout.addWidget(self.status_label)
        
        # Barra de progreso principal
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("%p%")
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #34495e;
                border-radius: 5px;
                text-align: center;
                font-size: 11pt;
                font-weight: bold;
                height: 25px;
            }
            QProgressBar::chunk {
                background-color: #3498db;
                border-radius: 3px;
            }
        """)
        layout.addWidget(self.progress_bar)
        
        # Información detallada
        info_layout = QVBoxLayout()
        info_layout.setSpacing(5)
        
        # Velocidad
        self.speed_label = QLabel("Velocidad: 0.0 MB/s")
        self.speed_label.setStyleSheet("font-size: 9pt; color: #95a5a6;")
        info_layout.addWidget(self.speed_label)
        
        # Tiempo restante
        self.time_label = QLabel("Tiempo restante: Calculando...")
        self.time_label.setStyleSheet("font-size: 9pt; color: #95a5a6;")
        info_layout.addWidget(self.time_label)
        
        # Archivos procesados
        self.files_label = QLabel("Archivos: 0 / 0")
        self.files_label.setStyleSheet("font-size: 9pt; color: #95a5a6;")
        info_layout.addWidget(self.files_label)
        
        layout.addLayout(info_layout)
        layout.addStretch()
        
        # Botón de cancelar
        if self.can_cancel:
            button_layout = QHBoxLayout()
            button_layout.addStretch()
            
            self.cancel_button = QPushButton("Cancelar")
            self.cancel_button.clicked.connect(self.cancel_operation)
            self.cancel_button.setStyleSheet("""
                QPushButton {
                    background-color: #e74c3c;
                    color: white;
                    border: none;
                    padding: 8px 20px;
                    border-radius: 4px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #c0392b;
                }
            """)
            button_layout.addWidget(self.cancel_button)
            
            layout.addLayout(button_layout)
        else:
            # Si no se puede cancelar, deshabilitar el botón de cerrar
            self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowCloseButtonHint)
    
    def start(self):
        """Iniciar el diálogo y comenzar a medir tiempo"""
        self.start_time = time.time()
        self.last_update_time = time.time()
        self.last_bytes = 0
        self.current_speed = 0.0
        self.show()
    
    def update_progress(self, value, total=None, status_text=None, bytes_transferred=0):
        """
        Actualizar el progreso
        
        Args:
            value: Valor actual (0-100) o bytes transferidos
            total: Valor total (si value es bytes) o None
            status_text: Texto de estado opcional
            bytes_transferred: Bytes transferidos (para calcular velocidad)
        """
        # Calcular porcentaje
        if total is not None and total > 0:
            percent = int((value / total) * 100)
            self.progress_bar.setMaximum(100)
            self.progress_bar.setValue(percent)
        else:
            # value ya es porcentaje
            self.progress_bar.setValue(min(100, max(0, int(value))))
        
        # Actualizar mensaje de estado
        if status_text:
            self.status_label.setText(status_text)
        
        # Calcular velocidad
        if bytes_transferred > 0:
            current_time = time.time()
            elapsed = current_time - self.last_update_time
            
            if elapsed > 0.5:  # Actualizar cada 0.5 segundos
                bytes_diff = bytes_transferred - self.last_bytes
                self.current_speed = bytes_diff / elapsed / (1024 * 1024)  # MB/s
                
                self.last_bytes = bytes_transferred
                self.last_update_time = current_time
                
                # Actualizar etiqueta de velocidad
                self.speed_label.setText(f"Velocidad: {self.current_speed:.2f} MB/s")
        
        # Calcular tiempo restante
        if self.start_time and self.progress_bar.value() > 0:
            elapsed_time = time.time() - self.start_time
            percent_done = self.progress_bar.value() / 100.0
            
            if percent_done > 0:
                total_estimated = elapsed_time / percent_done
                remaining = total_estimated - elapsed_time
                
                if remaining > 0:
                    minutes = int(remaining // 60)
                    seconds = int(remaining % 60)
                    self.time_label.setText(f"Tiempo restante: {minutes:02d}:{seconds:02d}")
                else:
                    self.time_label.setText("Tiempo restante: Finalizando...")
        
        # Actualizar archivos procesados si se proporciona
        if total is not None:
            self.files_label.setText(f"Archivos: {value} / {total}")
    
    def update_files_progress(self, current, total):
        """Actualizar progreso de archivos"""
        self.files_label.setText(f"Archivos: {current} / {total}")
    
    def set_status(self, text):
        """Establecer texto de estado"""
        self.status_label.setText(text)
    
    def cancel_operation(self):
        """Cancelar la operación"""
        self.cancelled.emit()
        self.reject()
    
    def finish(self, success=True, message="Completado"):
        """Finalizar el diálogo"""
        if success:
            self.status_label.setText(f"✅ {message}")
            self.progress_bar.setValue(100)
        else:
            self.status_label.setText(f"❌ {message}")
        
        # Ocultar información detallada
        self.speed_label.hide()
        self.time_label.hide()
        self.files_label.hide()
        
        # Cambiar botón de cancelar por cerrar
        if self.can_cancel:
            self.cancel_button.setText("Cerrar")
            self.cancel_button.clicked.disconnect()
            self.cancel_button.clicked.connect(self.accept)
        
        # Auto-cerrar después de 2 segundos si fue exitoso
        if success:
            QTimer.singleShot(2000, self.accept)


class SimpleProgressBar(QWidget):
    """
    Barra de progreso simple para usar en la UI principal
    (no es un diálogo modal)
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        """Configurar la interfaz"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        
        # Barra de progreso
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("%p%")
        layout.addWidget(self.progress_bar)
        
        # Etiqueta de estado
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("font-size: 9pt; color: #95a5a6;")
        layout.addWidget(self.status_label)
    
    def update_progress(self, value, status_text=None):
        """Actualizar progreso"""
        self.progress_bar.setValue(min(100, max(0, int(value))))
        if status_text:
            self.status_label.setText(status_text)
    
    def hide(self):
        """Ocultar el widget"""
        super().hide()
        self.progress_bar.setValue(0)
        self.status_label.setText("")

