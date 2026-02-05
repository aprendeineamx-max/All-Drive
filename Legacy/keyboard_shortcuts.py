"""
Gestor de Atajos de Teclado - VultrDrive Desktop
Mejora #56: Atajos de teclado para funciones principales
"""

from PyQt6.QtGui import QKeySequence, QShortcut
from PyQt6.QtCore import Qt

class KeyboardShortcuts:
    """
    Gestor de atajos de teclado para VultrDrive Desktop
    
    Atajos implementados:
    - Ctrl+M: Montar unidad
    - Ctrl+U: Desmontar unidad
    - Ctrl+S: Sincronizar ahora
    - Ctrl+,: Abrir configuración
    - Ctrl+Q: Salir
    - F1: Ayuda
    """
    
    def __init__(self, main_window):
        """
        Inicializar atajos de teclado
        
        Args:
            main_window: Instancia de MainWindow
        """
        self.main_window = main_window
        self.shortcuts = {}
        self.setup_shortcuts()
    
    def setup_shortcuts(self):
        """Configurar todos los atajos de teclado"""
        
        # Ctrl+M: Montar unidad
        if hasattr(self.main_window, 'mount_drive'):
            shortcut = QShortcut(QKeySequence("Ctrl+M"), self.main_window)
            shortcut.activated.connect(self.main_window.mount_drive)
            self.shortcuts['mount'] = shortcut
        
        # Ctrl+U: Desmontar unidad
        if hasattr(self.main_window, 'unmount_drive'):
            shortcut = QShortcut(QKeySequence("Ctrl+U"), self.main_window)
            shortcut.activated.connect(self.main_window.unmount_drive)
            self.shortcuts['unmount'] = shortcut
        
        # Ctrl+S: Sincronizar ahora
        if hasattr(self.main_window, 'start_real_time_sync'):
            shortcut = QShortcut(QKeySequence("Ctrl+S"), self.main_window)
            shortcut.activated.connect(self._toggle_sync)
            self.shortcuts['sync'] = shortcut
        
        # Ctrl+,: Abrir configuración
        if hasattr(self.main_window, 'open_settings'):
            shortcut = QShortcut(QKeySequence("Ctrl+,"), self.main_window)
            shortcut.activated.connect(self.main_window.open_settings)
            self.shortcuts['settings'] = shortcut
        
        # Ctrl+Q: Salir
        if hasattr(self.main_window, 'quit_application'):
            shortcut = QShortcut(QKeySequence("Ctrl+Q"), self.main_window)
            shortcut.activated.connect(self.main_window.quit_application)
            self.shortcuts['quit'] = shortcut
        
        # F1: Ayuda (mostrar atajos)
        shortcut = QShortcut(QKeySequence("F1"), self.main_window)
        shortcut.activated.connect(self.show_help)
        self.shortcuts['help'] = shortcut
    
    def _toggle_sync(self):
        """Toggle sincronización (iniciar si está detenida, detener si está activa)"""
        if hasattr(self.main_window, 'real_time_sync'):
            if self.main_window.real_time_sync and self.main_window.real_time_sync.is_running():
                if hasattr(self.main_window, 'stop_real_time_sync'):
                    self.main_window.stop_real_time_sync()
            else:
                if hasattr(self.main_window, 'start_real_time_sync'):
                    self.main_window.start_real_time_sync()
    
    def show_help(self):
        """Mostrar ayuda con atajos de teclado"""
        from PyQt6.QtWidgets import QMessageBox
        
        help_text = """
        <h3>⌨️ Atajos de Teclado</h3>
        <table>
        <tr><td><b>Ctrl+M</b></td><td>Montar unidad</td></tr>
        <tr><td><b>Ctrl+U</b></td><td>Desmontar unidad</td></tr>
        <tr><td><b>Ctrl+S</b></td><td>Sincronizar ahora</td></tr>
        <tr><td><b>Ctrl+,</b></td><td>Abrir configuración</td></tr>
        <tr><td><b>Ctrl+Q</b></td><td>Salir de la aplicación</td></tr>
        <tr><td><b>F1</b></td><td>Mostrar esta ayuda</td></tr>
        </table>
        """
        
        msg = QMessageBox(self.main_window)
        msg.setWindowTitle("Atajos de Teclado")
        msg.setTextFormat(Qt.TextFormat.RichText)
        msg.setText(help_text)
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec()
    
    def get_shortcuts_info(self) -> dict:
        """Obtener información de todos los atajos"""
        return {
            'mount': 'Ctrl+M',
            'unmount': 'Ctrl+U',
            'sync': 'Ctrl+S',
            'settings': 'Ctrl+,',
            'quit': 'Ctrl+Q',
            'help': 'F1'
        }

