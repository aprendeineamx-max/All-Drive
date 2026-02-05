from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
                             QComboBox, QLineEdit, QCheckBox, QGroupBox, QMessageBox)
from PyQt6.QtCore import Qt, pyqtSlot, QSize
from PyQt6.QtGui import QColor, QBrush, QIcon
from logger_manager import get_logger_manager
import time

class MonitoringTab(QWidget):
    def __init__(self):
        super().__init__()
        self.logger_manager = get_logger_manager()
        self.setup_ui()
        
        # Conectar señal de log
        self.logger_manager.log_received.connect(self.add_log_entry)
        
        # Cargar últimos logs del archivo (opcional, por ahora empezamos vacíos o leemos últimas lineas)
        # self.load_historical_logs()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Header
        header = QHBoxLayout()
        title = QLabel("📡 Centro de Monitoreo y Diagnóstico")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #007acc;")
        header.addWidget(title)
        header.addStretch()
        
        btn_upload = QPushButton("☁️ Subir Diagnóstico a Vultr")
        btn_upload.clicked.connect(self.upload_logs)
        btn_upload.setStyleSheet("background-color: #6f42c1; color: white;")
        header.addWidget(btn_upload)
        
        btn_clear = QPushButton("🧹 Limpiar Vista")
        btn_clear.clicked.connect(lambda: self.table_logs.setRowCount(0))
        header.addWidget(btn_clear)
        
        layout.addLayout(header)
        
        # Filtros
        filter_group = QGroupBox("Filtros y Búsqueda")
        filter_layout = QHBoxLayout()
        
        self.combo_level = QComboBox()
        self.combo_level.addItems(["Todos", "INFO", "WARNING", "ERROR", "DEBUG"])
        self.combo_level.currentTextChanged.connect(self.apply_filters)
        filter_layout.addWidget(QLabel("Nivel:"))
        filter_layout.addWidget(self.combo_level)
        
        self.txt_search = QLineEdit()
        self.txt_search.setPlaceholderText("Buscar mensaje...")
        self.txt_search.textChanged.connect(self.apply_filters)
        filter_layout.addWidget(QLabel("Buscar:"))
        filter_layout.addWidget(self.txt_search)
        
        self.chk_autoscroll = QCheckBox("Auto-Scroll")
        self.chk_autoscroll.setChecked(True)
        filter_layout.addWidget(self.chk_autoscroll)
        
        filter_group.setLayout(filter_layout)
        layout.addWidget(filter_group)
        
        # Tabla de Logs
        self.table_logs = QTableWidget()
        self.table_logs.setColumnCount(3)
        self.table_logs.setHorizontalHeaderLabels(["Hora", "Nivel", "Mensaje"])
        self.table_logs.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents) # Hora
        self.table_logs.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents) # Nivel
        self.table_logs.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)          # Mensaje
        
        # Estilo tabla
        self.table_logs.setStyleSheet("""
            QTableWidget {
                background-color: #1e1e1e;
                color: #d4d4d4;
                gridline-color: #333;
                font-family: Consolas;
            }
            QHeaderView::section {
                background-color: #2d2d2d;
                color: white;
                padding: 4px;
            }
        """)
        
        layout.addWidget(self.table_logs)

    @pyqtSlot(str, str, str)
    def add_log_entry(self, timestamp, level, message):
        row = self.table_logs.rowCount()
        self.table_logs.insertRow(row)
        
        # Items
        item_time = QTableWidgetItem(timestamp)
        item_level = QTableWidgetItem(level)
        item_msg = QTableWidgetItem(message)
        
        # Colores por nivel
        color = QColor("#d4d4d4") # Default text
        bg_color = QColor("#1e1e1e") # Default bg
        
        if "ERROR" in level or "CRITICAL" in level:
            color = QColor("#ff4444")
        elif "WARNING" in level:
            color = QColor("#ffbb33")
        elif "DEBUG" in level:
            color = QColor("#888888")
        elif "INFO" in level:
            color = QColor("#00ff00")
            
        for item in [item_time, item_level, item_msg]:
            item.setForeground(QBrush(color))
            # item.setBackground(QBrush(bg_color))
            item.setFlags(item.flags() ^ Qt.ItemFlag.ItemIsEditable) # Read only
            
        self.table_logs.setItem(row, 0, item_time)
        self.table_logs.setItem(row, 1, item_level)
        self.table_logs.setItem(row, 2, item_msg)
        
        # Aplicar filtro inmediato (ocultar si no cumple)
        if not self.check_filter(level, message):
            self.table_logs.setRowHidden(row, True)
            
        # Auto Scroll
        if self.chk_autoscroll.isChecked():
            self.table_logs.scrollToBottom()

    def check_filter(self, level, message):
        target_level = self.combo_level.currentText()
        search_text = self.txt_search.text().lower()
        
        # Nivel
        if target_level != "Todos" and target_level not in level:
            return False
            
        # Busqueda
        if search_text and search_text not in message.lower():
            return False
            
        return True

    def apply_filters(self):
        for row in range(self.table_logs.rowCount()):
            level = self.table_logs.item(row, 1).text()
            msg = self.table_logs.item(row, 2).text()
            
            should_show = self.check_filter(level, msg)
            self.table_logs.setRowHidden(row, not should_show)

    def upload_logs(self):
        btn = self.sender()
        btn.setEnabled(False)
        btn.setText("Subiendo...")
        
        ok, msg = self.logger_manager.upload_logs_to_cloud()
        
        if ok:
            QMessageBox.information(self, "Diagnóstico", "Logs subidos exitosamente a Vultr Drive.")
        else:
            QMessageBox.warning(self, "Error", f"Fallo al subir logs:\n{msg}")
            
        btn.setEnabled(True)
        btn.setText("☁️ Subir Diagnóstico a Vultr")
