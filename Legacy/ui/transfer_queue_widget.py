"""
Transfer Queue Widget - UI para mostrar múltiples transferencias con barras de progreso individuales
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QProgressBar, QScrollArea, QFrame, QGroupBox, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from transfer_manager import get_transfer_manager, TransferInfo, TransferStatus


class TransferItemWidget(QFrame):
    """Widget individual para una transferencia"""
    
    pause_clicked = pyqtSignal(str)  # transfer_id
    cancel_clicked = pyqtSignal(str)  # transfer_id
    resume_clicked = pyqtSignal(str)  # transfer_id
    
    def __init__(self, transfer: TransferInfo, parent=None):
        super().__init__(parent)
        self.transfer_id = transfer.id
        self.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)
        self.setStyleSheet("""
            TransferItemWidget {
                background-color: #1a1a2e;
                border: 1px solid #16213e;
                border-radius: 8px;
                margin: 2px;
                padding: 8px;
            }
        """)
        self.setup_ui(transfer)
    
    def setup_ui(self, transfer: TransferInfo):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(5)
        
        # Header: Name + Type Badge
        header = QHBoxLayout()
        
        # Type badge
        type_badges = {
            "azure_to_local": ("💾 Local", "#27ae60"),
            "azure_to_gcp": ("☁️ GCP", "#3498db"),
            "azure_to_azure": ("🔄 Azure", "#9b59b6"),
            "gcp_download": ("⬇️ GCP", "#1abc9c"),
        }
        badge_text, badge_color = type_badges.get(transfer.transfer_type, ("📥", "#7f8c8d"))
        
        self.type_badge = QLabel(badge_text)
        self.type_badge.setStyleSheet(f"""
            background-color: {badge_color};
            color: white;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: bold;
        """)
        header.addWidget(self.type_badge)
        
        # Name
        self.name_label = QLabel(transfer.name)
        self.name_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        self.name_label.setStyleSheet("color: #ecf0f1;")
        self.name_label.setWordWrap(True)
        header.addWidget(self.name_label, 1)
        
        layout.addLayout(header)
        
        # Destination
        self.dest_label = QLabel(f"→ {transfer.destination}")
        self.dest_label.setStyleSheet("color: #bdc3c7; font-size: 11px; margin-bottom: 4px;")
        self.dest_label.setWordWrap(True)
        layout.addWidget(self.dest_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(transfer.progress_percent)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: none;
                border-radius: 6px;
                background-color: #2c3e50;
                height: 24px;
                text-align: center;
                color: white;
                font-weight: bold;
                font-size: 12px;
            }
            QProgressBar::chunk {
                border-radius: 6px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3498db, stop:1 #2ecc71);
            }
        """)
        layout.addWidget(self.progress_bar)
        
        # Status text + Size info
        status_row = QHBoxLayout()
        
        self.status_label = QLabel(self._get_status_text(transfer))
        self.status_label.setStyleSheet("color: #bdc3c7; font-size: 12px; font-weight: 500;")
        status_row.addWidget(self.status_label, 1)
        
        # Size info
        bytes_dl = transfer.bytes_transferred / (1024**3)
        bytes_total = transfer.total_bytes / (1024**3) if transfer.total_bytes > 0 else 0
        self.size_label = QLabel(f"{bytes_dl:.2f} / {bytes_total:.2f} GB")
        self.size_label.setStyleSheet("color: #95a5a6; font-size: 12px; font-weight: bold;")
        status_row.addWidget(self.size_label)
        
        layout.addLayout(status_row)
        
        # Buttons
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        
        self.pause_btn = QPushButton("⏸️")
        self.pause_btn.setToolTip("Pausar")
        self.pause_btn.setFixedSize(36, 30)
        self.pause_btn.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
                border: none;
                border-radius: 5px;
                color: white;
                font-size: 14px;
            }
            QPushButton:hover { background-color: #e67e22; }
        """)
        self.pause_btn.clicked.connect(lambda: self.pause_clicked.emit(self.transfer_id))
        btn_row.addWidget(self.pause_btn)
        
        self.resume_btn = QPushButton("▶️")
        self.resume_btn.setToolTip("Reanudar")
        self.resume_btn.setFixedSize(36, 30)
        self.resume_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                border: none;
                border-radius: 5px;
                color: white;
                font-size: 14px;
            }
            QPushButton:hover { background-color: #2ecc71; }
        """)
        self.resume_btn.clicked.connect(lambda: self.resume_clicked.emit(self.transfer_id))
        self.resume_btn.hide()  # Hidden by default
        btn_row.addWidget(self.resume_btn)
        
        self.cancel_btn = QPushButton("✖️")
        self.cancel_btn.setToolTip("Cancelar")
        self.cancel_btn.setFixedSize(30, 24)
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                border: none;
                border-radius: 4px;
                color: white;
            }
            QPushButton:hover { background-color: #c0392b; }
        """)
        self.cancel_btn.clicked.connect(lambda: self.cancel_clicked.emit(self.transfer_id))
        btn_row.addWidget(self.cancel_btn)
        
        layout.addLayout(btn_row)
        
        self._update_button_visibility(transfer.status)
    
    def _get_status_text(self, transfer: TransferInfo) -> str:
        status_map = {
            "queued": "⏳ En cola...",
            "running": "🔄 Descargando...",
            "paused": "⏸️ Pausado",
            "completed": "✅ Completado",
            "error": f"❌ Error: {transfer.error_message or 'Desconocido'}",
            "cancelled": "🚫 Cancelado",
        }
        return status_map.get(transfer.status, transfer.status)
    
    def _update_button_visibility(self, status: str):
        if status == TransferStatus.RUNNING.value:
            self.pause_btn.show()
            self.resume_btn.hide()
            self.cancel_btn.show()
        elif status in [TransferStatus.PAUSED.value, TransferStatus.ERROR.value]:
            self.pause_btn.hide()
            self.resume_btn.show()
            self.cancel_btn.show()
        else:  # completed, cancelled, queued
            self.pause_btn.hide()
            self.resume_btn.hide()
            self.cancel_btn.hide() if status == TransferStatus.COMPLETED.value else self.cancel_btn.show()
    
    def update_progress(self, percent: int, status_text: str = ""):
        self.progress_bar.setValue(percent)
        if status_text:
            self.status_label.setText(status_text)
    
    def update_size(self, bytes_downloaded: int, total_bytes: int):
        gb_dl = bytes_downloaded / (1024**3)
        gb_total = total_bytes / (1024**3) if total_bytes > 0 else 0
        self.size_label.setText(f"{gb_dl:.2f} / {gb_total:.2f} GB")
    
    def set_finished(self, success: bool, message: str = ""):
        if success:
            self.status_label.setText("✅ Completado")
            self.status_label.setStyleSheet("color: #2ecc71; font-size: 10px;")
            self.progress_bar.setValue(100)
            self.progress_bar.setStyleSheet(self.progress_bar.styleSheet().replace("#3498db", "#2ecc71"))
        else:
            self.status_label.setText(f"❌ {message}")
            self.status_label.setStyleSheet("color: #e74c3c; font-size: 10px;")
        
        self._update_button_visibility(TransferStatus.COMPLETED.value if success else TransferStatus.ERROR.value)


class TransferQueueWidget(QWidget):
    """Widget contenedor para la cola de transferencias"""
    
    resume_requested = pyqtSignal(str)  # transfer_id
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.transfer_widgets: dict[str, TransferItemWidget] = {}
        self.manager = get_transfer_manager()
        self.setup_ui()
        self.connect_signals()
        self.load_existing_transfers()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Header
        header = QGroupBox("📥 Transferencias Activas")
        header.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 12px;
                color: #ecf0f1;
                border: 1px solid #34495e;
                border-radius: 6px;
                margin-top: 0px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(5, 15, 5, 5)
        
        # Scroll area for transfers
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)
        
        self.transfers_container = QWidget()
        self.transfers_layout = QVBoxLayout(self.transfers_container)
        self.transfers_layout.setContentsMargins(0, 0, 0, 0)
        self.transfers_layout.setSpacing(5)
        self.transfers_layout.addStretch()
        
        scroll.setWidget(self.transfers_container)
        header_layout.addWidget(scroll)
        
        # Empty state label
        self.empty_label = QLabel("No hay transferencias activas")
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_label.setStyleSheet("color: #7f8c8d; font-style: italic; padding: 20px;")
        self.transfers_layout.insertWidget(0, self.empty_label)
        
        layout.addWidget(header)
    
    def connect_signals(self):
        self.manager.transfer_added.connect(self.on_transfer_added)
        self.manager.transfer_updated.connect(self.on_transfer_updated)
        self.manager.transfer_finished.connect(self.on_transfer_finished)
        self.manager.transfer_removed.connect(self.on_transfer_removed)
    
    def load_existing_transfers(self):
        """Cargar transferencias existentes al iniciar"""
        for transfer in self.manager.get_all_transfers():
            self._add_transfer_widget(transfer)
    
    def _add_transfer_widget(self, transfer: TransferInfo):
        if transfer.id in self.transfer_widgets:
            return
        
        self.empty_label.hide()
        
        widget = TransferItemWidget(transfer)
        widget.pause_clicked.connect(self.on_pause_clicked)
        widget.cancel_clicked.connect(self.on_cancel_clicked)
        widget.resume_clicked.connect(self.on_resume_clicked)
        
        self.transfer_widgets[transfer.id] = widget
        # Insert before the stretch
        self.transfers_layout.insertWidget(self.transfers_layout.count() - 1, widget)
    
    def on_transfer_added(self, transfer_id: str):
        transfer = self.manager.get_transfer(transfer_id)
        if transfer:
            self._add_transfer_widget(transfer)
    
    def on_transfer_updated(self, transfer_id: str, progress: int, status_text: str):
        if transfer_id in self.transfer_widgets:
            widget = self.transfer_widgets[transfer_id]
            widget.update_progress(progress, status_text)
            
            transfer = self.manager.get_transfer(transfer_id)
            if transfer:
                widget.update_size(transfer.bytes_transferred, transfer.total_bytes)
    
    def on_transfer_finished(self, transfer_id: str, success: bool, message: str):
        if transfer_id in self.transfer_widgets:
            widget = self.transfer_widgets[transfer_id]
            widget.set_finished(success, message)
    
    def on_transfer_removed(self, transfer_id: str):
        if transfer_id in self.transfer_widgets:
            widget = self.transfer_widgets.pop(transfer_id)
            widget.deleteLater()
            
            if not self.transfer_widgets:
                self.empty_label.show()
    
    def on_pause_clicked(self, transfer_id: str):
        self.manager.pause_transfer(transfer_id)
        if transfer_id in self.transfer_widgets:
            self.transfer_widgets[transfer_id].status_label.setText("⏸️ Pausado")
            self.transfer_widgets[transfer_id]._update_button_visibility(TransferStatus.PAUSED.value)
    
    def on_cancel_clicked(self, transfer_id: str):
        self.manager.cancel_transfer(transfer_id)
    
    def on_resume_clicked(self, transfer_id: str):
        # Emit signal for parent to handle resume logic
        self.resume_requested.emit(transfer_id)
