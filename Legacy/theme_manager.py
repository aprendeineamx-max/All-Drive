# Theme Manager for VultrDriveDesktop
# Autor: GitHub Copilot Assistant

class ThemeManager:
    def __init__(self):
        self.current_theme = 'dark'
        self.themes = {
            'dark': {
                'name': 'Dark Theme',
                'stylesheet': """
/* Dark Theme */
QWidget {
    background-color: #2b2b2b;
    color: #ffffff;
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 10pt;
}

QMainWindow {
    background-color: #2b2b2b;
}

QPushButton {
    background-color: #007acc;
    color: #ffffff;
    border: 1px solid #007acc;
    padding: 8px 16px;
    border-radius: 4px;
    font-size: 10pt;
    font-weight: bold;
}

QPushButton:hover {
    background-color: #005f9e;
    border: 1px solid #005f9e;
}

QPushButton:pressed {
    background-color: #004c7d;
}

QPushButton:disabled {
    background-color: #555555;
    color: #888888;
    border: 1px solid #555555;
}

/* Language and Theme buttons */
QPushButton#languageButton, QPushButton#themeButton, QPushButton#closeWithoutUnmountButton {
    background-color: #6c757d;
    border: 1px solid #6c757d;
    padding: 6px 12px;
    font-size: 9pt;
}

QPushButton#languageButton:hover, QPushButton#themeButton:hover, QPushButton#closeWithoutUnmountButton:hover {
    background-color: #5a6268;
    border: 1px solid #5a6268;
}

/* Botón de cerrar sin desmontar - color ligeramente diferente */
QPushButton#closeWithoutUnmountButton {
    background-color: #e67e22;
    border: 1px solid #e67e22;
}

QPushButton#closeWithoutUnmountButton:hover {
    background-color: #d35400;
    border: 1px solid #d35400;
}

QComboBox {
    background-color: #3c3c3c;
    border: 1px solid #555555;
    padding: 5px;
    border-radius: 4px;
    color: #ffffff;
}

QComboBox::drop-down {
    border: none;
}

QComboBox::down-arrow {
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 5px solid #ffffff;
}

QComboBox QAbstractItemView {
    background-color: #3c3c3c;
    selection-background-color: #007acc;
    color: #ffffff;
    border: 1px solid #555555;
}

QLabel {
    font-size: 10pt;
    padding-bottom: 5px;
    color: #ffffff;
}

QLineEdit {
    background-color: #3c3c3c;
    border: 1px solid #555555;
    padding: 6px;
    border-radius: 4px;
    color: #ffffff;
}

QLineEdit:focus {
    border: 1px solid #007acc;
}

QTextEdit {
    background-color: #3c3c3c;
    border: 1px solid #555555;
    padding: 6px;
    border-radius: 4px;
    color: #ffffff;
}

QStatusBar {
    background-color: #007acc;
    color: #ffffff;
}

QStatusBar::item {
    border: none;
}

QFormLayout > QLabel {
    font-weight: bold;
}

QListWidget {
    background-color: #3c3c3c;
    border: 1px solid #555555;
    padding: 5px;
    border-radius: 4px;
}

QListWidget::item {
    padding: 5px;
}

QListWidget::item:selected {
    background-color: #007acc;
}

QGroupBox {
    border: 2px solid #555555;
    border-radius: 5px;
    margin-top: 10px;
    font-weight: bold;
    padding-top: 10px;
    color: #ffffff;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 5px;
    color: #ffffff;
}

QTabWidget::pane {
    border: 1px solid #555555;
    border-radius: 4px;
    top: -1px;
    background-color: #2b2b2b;
}

QTabBar::tab {
    background-color: #3c3c3c;
    color: #ffffff;
    padding: 8px 16px;
    border: 1px solid #555555;
    border-bottom: none;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
}

QTabBar::tab:selected {
    background-color: #007acc;
}

QTabBar::tab:hover {
    background-color: #005f9e;
}

QProgressBar {
    border: 1px solid #555555;
    border-radius: 4px;
    text-align: center;
    background-color: #3c3c3c;
    color: #ffffff;
}

QProgressBar::chunk {
    background-color: #007acc;
    border-radius: 3px;
}

QMessageBox {
    background-color: #2b2b2b;
}

QMessageBox QLabel {
    color: #ffffff;
}

QMessageBox QPushButton {
    min-width: 80px;
}

QScrollBar:vertical {
    background-color: #3c3c3c;
    width: 12px;
    border-radius: 6px;
}

QScrollBar::handle:vertical {
    background-color: #555555;
    border-radius: 6px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background-color: #777777;
}

QScrollBar:horizontal {
    background-color: #3c3c3c;
    height: 12px;
    border-radius: 6px;
}

QScrollBar::handle:horizontal {
    background-color: #555555;
    border-radius: 6px;
    min-width: 20px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #777777;
}
"""
            },
            'light': {
                'name': 'Light Theme',
                'stylesheet': """
/* Light Theme */
QWidget {
    background-color: #ffffff;
    color: #333333;
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 10pt;
}

QMainWindow {
    background-color: #ffffff;
}

QPushButton {
    background-color: #0078d4;
    color: #ffffff;
    border: 1px solid #0078d4;
    padding: 8px 16px;
    border-radius: 4px;
    font-size: 10pt;
    font-weight: bold;
}

QPushButton:hover {
    background-color: #106ebe;
    border: 1px solid #106ebe;
}

QPushButton:pressed {
    background-color: #005a9e;
}

QPushButton:disabled {
    background-color: #cccccc;
    color: #666666;
    border: 1px solid #cccccc;
}

/* Language and Theme buttons */
QPushButton#languageButton, QPushButton#themeButton {
    background-color: #6c757d;
    border: 1px solid #6c757d;
    padding: 6px 12px;
    font-size: 9pt;
    color: #ffffff;
}

QPushButton#languageButton:hover, QPushButton#themeButton:hover {
    background-color: #5a6268;
    border: 1px solid #5a6268;
}

QComboBox {
    background-color: #ffffff;
    border: 1px solid #cccccc;
    padding: 5px;
    border-radius: 4px;
    color: #333333;
}

QComboBox::drop-down {
    border: none;
}

QComboBox::down-arrow {
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 5px solid #333333;
}

QComboBox QAbstractItemView {
    background-color: #ffffff;
    selection-background-color: #0078d4;
    selection-color: #ffffff;
    color: #333333;
    border: 1px solid #cccccc;
}

QLabel {
    font-size: 10pt;
    padding-bottom: 5px;
    color: #333333;
}

QLineEdit {
    background-color: #ffffff;
    border: 1px solid #cccccc;
    padding: 6px;
    border-radius: 4px;
    color: #333333;
}

QLineEdit:focus {
    border: 1px solid #0078d4;
}

QTextEdit {
    background-color: #ffffff;
    border: 1px solid #cccccc;
    padding: 6px;
    border-radius: 4px;
    color: #333333;
}

QStatusBar {
    background-color: #0078d4;
    color: #ffffff;
}

QStatusBar::item {
    border: none;
}

QFormLayout > QLabel {
    font-weight: bold;
}

QListWidget {
    background-color: #ffffff;
    border: 1px solid #cccccc;
    padding: 5px;
    border-radius: 4px;
}

QListWidget::item {
    padding: 5px;
}

QListWidget::item:selected {
    background-color: #0078d4;
    color: #ffffff;
}

QGroupBox {
    border: 2px solid #cccccc;
    border-radius: 5px;
    margin-top: 10px;
    font-weight: bold;
    padding-top: 10px;
    color: #333333;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 5px;
    color: #333333;
}

QTabWidget::pane {
    border: 1px solid #cccccc;
    border-radius: 4px;
    top: -1px;
    background-color: #ffffff;
}

QTabBar::tab {
    background-color: #f0f0f0;
    color: #333333;
    padding: 8px 16px;
    border: 1px solid #cccccc;
    border-bottom: none;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
}

QTabBar::tab:selected {
    background-color: #0078d4;
    color: #ffffff;
}

QTabBar::tab:hover {
    background-color: #e6e6e6;
}

QProgressBar {
    border: 1px solid #cccccc;
    border-radius: 4px;
    text-align: center;
    background-color: #f0f0f0;
    color: #333333;
}

QProgressBar::chunk {
    background-color: #0078d4;
    border-radius: 3px;
}

QMessageBox {
    background-color: #ffffff;
}

QMessageBox QLabel {
    color: #333333;
}

QMessageBox QPushButton {
    min-width: 80px;
}

QScrollBar:vertical {
    background-color: #f0f0f0;
    width: 12px;
    border-radius: 6px;
}

QScrollBar::handle:vertical {
    background-color: #cccccc;
    border-radius: 6px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background-color: #999999;
}

QScrollBar:horizontal {
    background-color: #f0f0f0;
    height: 12px;
    border-radius: 6px;
}

QScrollBar::handle:horizontal {
    background-color: #cccccc;
    border-radius: 6px;
    min-width: 20px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #999999;
}
"""
            }
        }
    
    def set_theme(self, theme_name):
        """Change the current theme"""
        if theme_name in self.themes:
            self.current_theme = theme_name
            return True
        return False
    
    def get_current_stylesheet(self):
        """Get the stylesheet for the current theme"""
        return self.themes[self.current_theme]['stylesheet']
    
    def get_available_themes(self):
        """Get list of available themes"""
        return {
            'dark': '🌙 Dark Theme',
            'light': '☀️ Light Theme'
        }
    
    def get_current_theme_name(self):
        """Get the display name of the current theme"""
        return self.themes[self.current_theme]['name']