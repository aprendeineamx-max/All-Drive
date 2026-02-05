from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QMessageBox,
    QLabel,
    QSizePolicy,
)
from PyQt6.QtCore import Qt, QTimer, QDateTime, pyqtSignal


class MultiMountsWidget(QWidget):
    """Widget para visualizar y gestionar múltiples montajes activos."""

    request_new_mount = pyqtSignal()

    def __init__(self, mount_manager, translator=None, parent=None):
        super().__init__(parent)
        self.mount_manager = mount_manager
        self.translator = translator
        self._setup_ui()
        self.refresh_table(defer=True)

    def tr(self, key, fallback=None):
        if self.translator:
            value = self.translator.get(key)
            if value != key:
                return value
        return fallback or key

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(0, 0, 0, 0)

        self.title_label = QLabel(self.tr("multi_mounts_title", "📊 Gestor de Unidades Montadas"))
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.title_label.setObjectName("multiMountsTitle")
        layout.addWidget(self.title_label)

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels([
            self.tr("multi_mount_status_header", "Estado"),
            self.tr("multi_mount_letter_header", "Letra"),
            self.tr("multi_mount_bucket_header", "Bucket"),
            self.tr("multi_mount_profile_header", "Perfil"),
            self.tr("multi_mount_actions_header", "Acciones"),
        ])
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionMode(self.table.SelectionMode.NoSelection)
        self.table.setEditTriggers(self.table.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        layout.addWidget(self.table)

        self.summary_label = QLabel()
        self.summary_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.summary_label.setObjectName("multiMountsSummary")
        layout.addWidget(self.summary_label)

        btn_layout = QHBoxLayout()
        self.btn_mount_new = QPushButton(self.tr("multi_mount_new_button", "➕ Montar Nuevo"))
        self.btn_refresh = QPushButton(self.tr("multi_mount_refresh_button", "🔄 Actualizar"))
        self.btn_unmount_all = QPushButton(self.tr("multi_mount_unmount_all_button", "🗑 Desmontar Todos"))

        self.btn_refresh.clicked.connect(self.refresh_table)
        self.btn_unmount_all.clicked.connect(self._confirm_unmount_all)
        self.btn_mount_new.clicked.connect(self.request_new_mount.emit)
        btn_layout.addWidget(self.btn_mount_new)
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_refresh)
        btn_layout.addWidget(self.btn_unmount_all)
        layout.addLayout(btn_layout)

    def refresh_table(self, defer=False):
        if defer:
            QTimer.singleShot(1000, self.refresh_table)
            return

        if hasattr(self.mount_manager, "refresh_all_status"):
            self.mount_manager.refresh_all_status()

        self.table.setRowCount(0)
        mounts = self.mount_manager.get_mounts_list()
        connected = 0

        for info in mounts:
            letter = info.letter
            row = self.table.rowCount()
            self.table.insertRow(row)
            status = info.status or 'disconnected'
            if status == 'connected':
                icon = "✅"
                connected += 1
            elif status == 'error':
                icon = "⚠️"
            else:
                icon = "⏸"
            self.table.setItem(row, 0, QTableWidgetItem(icon))
            self.table.setItem(row, 1, QTableWidgetItem(f"{letter}:"))
            self.table.setItem(row, 2, QTableWidgetItem(info.bucket or "-"))
            self.table.setItem(row, 3, QTableWidgetItem(info.profile or "-"))

            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(0, 0, 0, 0)
            actions_layout.setSpacing(4)
            btn_open = QPushButton("📂")
            btn_unmount = QPushButton("🗑")
            btn_open.setToolTip(self.tr("multi_mount_open_tooltip", "Abrir en Explorador"))
            base_unmount_tooltip = self.tr("multi_mount_unmount_tooltip", "Desmontar")
            tooltip_unmount = base_unmount_tooltip
            btn_open.setEnabled(status == 'connected')
            btn_unmount.setEnabled(status != 'mounting')
            if info.error_message:
                tooltip_unmount = f"{base_unmount_tooltip}\n{info.error_message}"
            btn_unmount.setToolTip(tooltip_unmount)
            btn_open.clicked.connect(lambda _, l=letter: self._open_drive(l))
            btn_unmount.clicked.connect(lambda _, l=letter: self._unmount_drive(l))
            actions_layout.addWidget(btn_open)
            actions_layout.addWidget(btn_unmount)
            actions_layout.addStretch()
            self.table.setCellWidget(row, 4, actions_widget)

        self.table.resizeRowsToContents()
        total = len(mounts)
        last_updated = QDateTime.currentDateTime().toString("hh:mm:ss")
        self.summary_label.setText(
            self.tr(
                "multi_mount_summary",
                "Montajes activos: {}/{} (actualizado a las {})"
            ).format(connected, total, last_updated)
        )

    def update_translations(self):
        self.title_label.setText(self.tr("multi_mounts_title", "📊 Gestor de Unidades Montadas"))
        self.table.setHorizontalHeaderLabels([
            self.tr("multi_mount_status_header", "Estado"),
            self.tr("multi_mount_letter_header", "Letra"),
            self.tr("multi_mount_bucket_header", "Bucket"),
            self.tr("multi_mount_profile_header", "Perfil"),
            self.tr("multi_mount_actions_header", "Acciones"),
        ])
        self.btn_mount_new.setText(self.tr("multi_mount_new_button", "➕ Montar Nuevo"))
        self.btn_refresh.setText(self.tr("multi_mount_refresh_button", "🔄 Actualizar"))
        self.btn_unmount_all.setText(self.tr("multi_mount_unmount_all_button", "🗑 Desmontar Todos"))
        self.refresh_table()

    def _open_drive(self, letter):
        ok, message = self.mount_manager.open_drive_in_explorer(letter)
        if not ok:
            QMessageBox.warning(self, self.tr("warning", "Advertencia"), message)

    def _unmount_drive(self, letter):
        ok, message = self.mount_manager.unmount_drive(letter)
        if ok:
            self.refresh_table()
        else:
            QMessageBox.warning(self, self.tr("warning", "Advertencia"), message)

    def _confirm_unmount_all(self):
        reply = QMessageBox.question(
            self,
            self.tr("confirm_unmount_all_title", "Confirmar Desmontaje"),
            self.tr("confirm_unmount_all_text", "¿Deseas desmontar TODAS las unidades montadas?"),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            ok, message = self.mount_manager.unmount_all()
            if ok:
                QMessageBox.information(self, self.tr("success", "Éxito"), message)
            else:
                QMessageBox.warning(self, self.tr("warning", "Advertencia"), message)
            self.refresh_table()
