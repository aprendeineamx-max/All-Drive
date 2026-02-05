# Splash screen con tipografía adaptable
from PyQt6.QtWidgets import QSplashScreen
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap, QPainter, QColor, QFont, QFontMetrics, QKeyEvent


class FastSplashScreen(QSplashScreen):
    def __init__(self, title=None, subtitle=None):
        canvas = QPixmap(720, 360)
        canvas.fill(Qt.GlobalColor.transparent)

        super().__init__(canvas, Qt.WindowType.WindowStaysOnTopHint)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self._title = title or "Vultr Drive Desktop"
        self._subtitle = subtitle or "Productividad conectada a la nube"
        self._message = ""
        self._message_color = QColor(210, 220, 235)
        self._message_alignment = Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignBottom
        
        # ===== MEJORA: Timeout automático y soporte ESC =====
        self._auto_close_timer = QTimer()
        self._auto_close_timer.setSingleShot(True)
        self._auto_close_timer.timeout.connect(self._force_close)
        self._auto_close_timer.start(5000)  # Cerrar automáticamente después de 5 segundos
    
    def _force_close(self):
        """Forzar cierre del splash"""
        self.close()
    
    def keyPressEvent(self, event: QKeyEvent):
        """Permitir cerrar con ESC"""
        if event.key() == Qt.Key.Key_Escape:
            self._auto_close_timer.stop()
            self._force_close()
        else:
            super().keyPressEvent(event)

    def showMessage(self, message, alignment=Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignBottom, color=QColor(210, 220, 235)):
        self._message = message or ""
        self._message_alignment = alignment
        candidate_color = QColor(color)
        self._message_color = candidate_color if candidate_color.isValid() else QColor(210, 220, 235)
        self.update()

    def clearMessage(self):
        self._message = ""
        self.update()

    def setTitle(self, title: str):
        self._title = title or self._title
        self.update()

    def setSubtitle(self, subtitle: str):
        self._subtitle = subtitle or self._subtitle
        self.update()

    def _fit_font(self, family, text, max_width, max_point, min_point):
        font = QFont(family)
        for size in range(max_point, min_point - 1, -2):
            font.setPointSize(size)
            if QFontMetrics(font).horizontalAdvance(text) <= max_width:
                return font
        font.setPointSize(min_point)
        return font

    def drawContents(self, painter):
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), Qt.GlobalColor.transparent)

        outer = self.rect().adjusted(24, 24, -24, -24)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(22, 24, 32, 245))
        painter.drawRoundedRect(outer, 26, 26)

        accent_pen = QColor(52, 152, 219)
        painter.setPen(QColor(accent_pen))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(outer.adjusted(1, 1, -1, -1), 25, 25)

        inner = outer.adjusted(40, 36, -40, -36)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(34, 36, 44, 200))
        painter.drawRoundedRect(inner, 20, 20)

        # Estimar tipografía del título según ancho disponible
        title_rect = inner.adjusted(32, 36, -32, -inner.height() // 2)
        title_font = self._fit_font("Segoe UI Semibold", self._title, title_rect.width(), 44, 24)
        painter.setFont(title_font)
        painter.setPen(QColor(250, 252, 255))
        painter.drawText(title_rect, int(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter), self._title)

        # Subtítulo más discreto
        subtitle_rect = inner.adjusted(40, inner.height() // 2 - 10, -40, -inner.height() // 3)
        subtitle_font = self._fit_font("Segoe UI", self._subtitle, subtitle_rect.width(), 18, 12)
        painter.setFont(subtitle_font)
        painter.setPen(QColor(155, 170, 190))
        painter.drawText(subtitle_rect, int(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop | Qt.TextFlag.TextWordWrap), self._subtitle)

        # Mensaje de estado responsivo
        status_rect = inner.adjusted(40, inner.height() - 120, -40, -40)
        status_font = self._fit_font("Segoe UI", self._message, status_rect.width(), 16, 11) if self._message else QFont("Segoe UI", 12)
        painter.setFont(status_font)
        painter.setPen(self._message_color)
        painter.drawText(status_rect, int(self._message_alignment) | int(Qt.TextFlag.TextWordWrap), self._message)
