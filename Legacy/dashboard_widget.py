"""
Dashboard Widget - VultrDrive Desktop
Mejora #52: Dashboard con estadísticas visuales
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QProgressBar, QGroupBox, QGridLayout)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont
from datetime import datetime
import os

class DashboardWidget(QWidget):
    """
    Widget de Dashboard con estadísticas visuales
    
    Muestra:
    - Espacio usado/disponible (gráfico circular)
    - Archivos sincronizados hoy (contador)
    - Velocidad de transferencia actual (gráfico de línea)
    - Última sincronización (timestamp)
    - Estado de unidades montadas (iconos)
    """
    
    # Señal para actualizar datos
    update_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.translations = getattr(parent, "translations", None)
        self.setup_ui()
        self.stats = {
            'space_used': 0,
            'space_total': 0,
            'files_synced_today': 0,
            'transfer_speed': 0.0,
            'last_sync': None,
            'mounted_drives': []
        }
        
        # Timer para actualización automática
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_requested.emit)
        self.update_timer.start(30000)  # Actualizar cada 30 segundos
    
    def setup_ui(self):
        """Configurar la interfaz del dashboard"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Título
        title = QLabel(self.tr("dashboard_tab_title"))
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Grid para estadísticas
        grid = QGridLayout()
        grid.setSpacing(15)
        
        # 1. Espacio usado/disponible
        space_group = self.create_space_widget()
        grid.addWidget(space_group, 0, 0, 1, 2)
        
        # 2. Archivos sincronizados hoy
        files_group = self.create_files_widget()
        grid.addWidget(files_group, 0, 2, 1, 1)
        
        # 3. Velocidad de transferencia
        speed_group = self.create_speed_widget()
        grid.addWidget(speed_group, 1, 0, 1, 1)
        
        # 4. Última sincronización
        sync_group = self.create_sync_widget()
        grid.addWidget(sync_group, 1, 1, 1, 1)
        
        # 5. Unidades montadas
        drives_group = self.create_drives_widget()
        grid.addWidget(drives_group, 1, 2, 1, 1)
        
        layout.addLayout(grid)
        layout.addStretch()
    
    def create_space_widget(self) -> QGroupBox:
        """Crear widget de espacio usado/disponible"""
        group = QGroupBox(self.tr("dashboard_space_group"))
        layout = QVBoxLayout()
        
        # Barra de progreso circular (simulada con barra horizontal)
        self.space_progress = QProgressBar()
        self.space_progress.setMinimum(0)
        self.space_progress.setMaximum(100)
        self.space_progress.setValue(0)
        self.space_progress.setFormat("%p%")
        self.space_progress.setStyleSheet("""
            QProgressBar {
                border: 2px solid #34495e;
                border-radius: 5px;
                text-align: center;
                font-size: 12pt;
                font-weight: bold;
                height: 30px;
            }
            QProgressBar::chunk {
                background-color: #3498db;
                border-radius: 3px;
            }
        """)
        layout.addWidget(self.space_progress)
        
        # Información de espacio
        self.space_label = QLabel(self.tr("dashboard_space_initial"))
        self.space_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.space_label.setStyleSheet("font-size: 11pt; color: #95a5a6;")
        layout.addWidget(self.space_label)
        
        # Porcentaje
        self.space_percent = QLabel(self.tr("dashboard_space_percent").format(0))
        self.space_percent.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.space_percent.setStyleSheet("font-size: 10pt; color: #7f8c8d;")
        layout.addWidget(self.space_percent)
        
        group.setLayout(layout)
        return group
    
    def create_files_widget(self) -> QGroupBox:
        """Crear widget de archivos sincronizados"""
        group = QGroupBox(self.tr("dashboard_files_group"))
        layout = QVBoxLayout()
        
        # Contador grande
        self.files_count = QLabel("0")
        self.files_count.setAlignment(Qt.AlignmentFlag.AlignCenter)
        count_font = QFont()
        count_font.setPointSize(32)
        count_font.setBold(True)
        self.files_count.setFont(count_font)
        self.files_count.setStyleSheet("color: #2ecc71;")
        layout.addWidget(self.files_count)
        
        # Etiqueta
        files_label = QLabel(self.tr("dashboard_files_subtext"))
        files_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        files_label.setStyleSheet("font-size: 10pt; color: #95a5a6;")
        layout.addWidget(files_label)
        
        group.setLayout(layout)
        return group
    
    def create_speed_widget(self) -> QGroupBox:
        """Crear widget de velocidad de transferencia"""
        group = QGroupBox(self.tr("dashboard_speed_group"))
        layout = QVBoxLayout()
        
        # Velocidad actual
        self.speed_label = QLabel(self.tr("dashboard_speed_zero"))
        self.speed_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        speed_font = QFont()
        speed_font.setPointSize(18)
        speed_font.setBold(True)
        self.speed_label.setFont(speed_font)
        self.speed_label.setStyleSheet("color: #f39c12;")
        layout.addWidget(self.speed_label)
        
        # Estado
        self.speed_status = QLabel(self.tr("dashboard_speed_idle"))
        self.speed_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.speed_status.setStyleSheet("font-size: 9pt; color: #7f8c8d;")
        layout.addWidget(self.speed_status)
        
        group.setLayout(layout)
        return group
    
    def create_sync_widget(self) -> QGroupBox:
        """Crear widget de última sincronización"""
        group = QGroupBox(self.tr("dashboard_sync_group"))
        layout = QVBoxLayout()
        
        # Última sincronización
        self.last_sync_label = QLabel(self.tr("dashboard_sync_never"))
        self.last_sync_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sync_font = QFont()
        sync_font.setPointSize(12)
        self.last_sync_label.setFont(sync_font)
        self.last_sync_label.setStyleSheet("color: #95a5a6;")
        layout.addWidget(self.last_sync_label)
        
        # Estado
        self.sync_status = QLabel(self.tr("dashboard_sync_stopped"))
        self.sync_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.sync_status.setStyleSheet("font-size: 10pt; color: #e74c3c;")
        layout.addWidget(self.sync_status)
        
        group.setLayout(layout)
        return group
    
    def create_drives_widget(self) -> QGroupBox:
        """Crear widget de unidades montadas"""
        group = QGroupBox(self.tr("dashboard_drives_group"))
        layout = QVBoxLayout()
        
        # Lista de unidades
        self.drives_label = QLabel(self.tr("dashboard_drives_none"))
        self.drives_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.drives_label.setStyleSheet("font-size: 11pt; color: #95a5a6;")
        layout.addWidget(self.drives_label)
        
        # Contador
        self.drives_count = QLabel(self.tr("dashboard_drives_count").format(0))
        self.drives_count.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.drives_count.setStyleSheet("font-size: 9pt; color: #7f8c8d;")
        layout.addWidget(self.drives_count)
        
        group.setLayout(layout)
        return group
    
    def update_stats(self, stats: dict):
        """
        Actualizar estadísticas del dashboard
        
        Args:
            stats: Diccionario con estadísticas:
                - space_used: Espacio usado en bytes
                - space_total: Espacio total en bytes
                - files_synced_today: Archivos sincronizados hoy
                - transfer_speed: Velocidad en MB/s
                - last_sync: Timestamp de última sincronización
                - mounted_drives: Lista de letras de unidades montadas
        """
        self.stats.update(stats)
        self._update_ui()
    
    def _update_ui(self):
        """Actualizar la UI con las estadísticas actuales"""
        # Espacio
        space_used = self.stats.get('space_used', 0)
        space_total = self.stats.get('space_total', 0)
        
        if space_total > 0:
            percent = int((space_used / space_total) * 100)
            self.space_progress.setValue(percent)
            
            # Formatear tamaños
            used_mb = space_used / (1024 * 1024)
            total_mb = space_total / (1024 * 1024)
            
            if total_mb > 1024:
                used_gb = used_mb / 1024
                total_gb = total_mb / 1024
                self.space_label.setText(f"{used_gb:.2f} GB / {total_gb:.2f} GB")
            else:
                self.space_label.setText(f"{used_mb:.2f} MB / {total_mb:.2f} MB")
            
            self.space_percent.setText(f"{percent}% usado")
        else:
            self.space_progress.setValue(0)
            self.space_label.setText(self.tr("dashboard_space_unavailable"))
            self.space_percent.setText(self.tr("dashboard_space_percent").format(0))
        
        # Archivos
        files_count = self.stats.get('files_synced_today', 0)
        self.files_count.setText(str(files_count))
        
        # Velocidad
        speed = self.stats.get('transfer_speed', 0.0)
        if speed > 0:
            self.speed_label.setText(f"{speed:.2f} MB/s")
            self.speed_status.setText(self.tr("dashboard_speed_active"))
            self.speed_status.setStyleSheet("font-size: 9pt; color: #2ecc71;")
        else:
            self.speed_label.setText(self.tr("dashboard_speed_zero"))
            self.speed_status.setText(self.tr("dashboard_speed_idle"))
            self.speed_status.setStyleSheet("font-size: 9pt; color: #7f8c8d;")
        
        # Última sincronización
        last_sync = self.stats.get('last_sync')
        if last_sync:
            if isinstance(last_sync, datetime):
                time_str = last_sync.strftime("%H:%M:%S")
                date_str = last_sync.strftime("%d/%m/%Y")
                self.last_sync_label.setText(f"{time_str}\n{date_str}")
            else:
                self.last_sync_label.setText(str(last_sync))
            self.sync_status.setText(self.tr("dashboard_sync_active"))
            self.sync_status.setStyleSheet("font-size: 10pt; color: #2ecc71;")
        else:
            self.last_sync_label.setText(self.tr("dashboard_sync_never"))
            self.sync_status.setText(self.tr("dashboard_sync_stopped"))
            self.sync_status.setStyleSheet("font-size: 10pt; color: #e74c3c;")
        
        # Unidades montadas
        drives = self.stats.get('mounted_drives', [])
        if drives:
            drives_str = ", ".join([f"{d}:" for d in drives])
            self.drives_label.setText(drives_str)
            self.drives_count.setText(self.tr("dashboard_drives_count").format(len(drives)))
        else:
            self.drives_label.setText(self.tr("dashboard_drives_none"))
            self.drives_count.setText(self.tr("dashboard_drives_count").format(0))

    def tr(self, key):
        if self.translations:
            return self.translations.get(key)
        return key

