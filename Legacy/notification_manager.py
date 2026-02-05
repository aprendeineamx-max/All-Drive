"""
Gestor de Notificaciones - VultrDrive Desktop
Sistema de notificaciones de escritorio nativas de Windows
"""

from PyQt6.QtWidgets import QSystemTrayIcon
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtGui import QIcon
from enum import Enum
from datetime import datetime

class NotificationType(Enum):
    """Tipos de notificaciones"""
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"


class NotificationManager(QObject):
    """
    Gestor de notificaciones de escritorio
    Utiliza QSystemTrayIcon para mostrar notificaciones nativas
    """
    
    # Señal emitida cuando se hace clic en una notificación
    notification_clicked = pyqtSignal(str)  # notification_id
    
    def __init__(self, tray_icon: QSystemTrayIcon = None, translations=None):
        super().__init__()
        self.tray_icon = tray_icon
        self.translations = translations
        self.enabled = True
        self.duration = 5000  # Duración en ms (5 segundos por defecto)
        self.notification_history = []
        self.max_history = 50
        
        # Configuración por tipo de notificación
        self.enabled_types = {
            NotificationType.INFO: True,
            NotificationType.SUCCESS: True,
            NotificationType.WARNING: True,
            NotificationType.ERROR: True
        }
    
    def set_tray_icon(self, tray_icon: QSystemTrayIcon):
        """Establecer el icono de bandeja para mostrar notificaciones"""
        self.tray_icon = tray_icon
        if self.tray_icon:
            self.tray_icon.messageClicked.connect(self._on_notification_clicked)
    
    def is_available(self) -> bool:
        """Verificar si las notificaciones están disponibles"""
        return self.tray_icon is not None and QSystemTrayIcon.isSystemTrayAvailable()
    
    def set_enabled(self, enabled: bool):
        """Habilitar o deshabilitar todas las notificaciones"""
        self.enabled = enabled
    
    def set_type_enabled(self, notification_type: NotificationType, enabled: bool):
        """Habilitar/deshabilitar un tipo específico de notificación"""
        self.enabled_types[notification_type] = enabled
    
    def set_duration(self, duration_ms: int):
        """Establecer duración de las notificaciones en milisegundos"""
        self.duration = max(1000, min(10000, duration_ms))  # Entre 1 y 10 segundos
    
    def show(
        self, 
        title: str, 
        message: str, 
        notification_type: NotificationType = NotificationType.INFO,
        duration: int = None
    ) -> bool:
        """
        Mostrar una notificación
        
        Args:
            title: Título de la notificación
            message: Mensaje de la notificación
            notification_type: Tipo de notificación (INFO, SUCCESS, WARNING, ERROR)
            duration: Duración en ms (None = usar duración por defecto)
            
        Returns:
            True si se mostró, False si no
        """
        # Verificar si está habilitado
        if not self.enabled or not self.enabled_types.get(notification_type, True):
            return False
        
        # Verificar disponibilidad
        if not self.is_available():
            print(f"[Notification] {title}: {message}")
            return False
        
        # Determinar icono según tipo
        icon_type = self._get_icon_type(notification_type)
        
        # Duración
        show_duration = duration if duration is not None else self.duration
        
        # Mostrar notificación
        try:
            self.tray_icon.showMessage(
                title,
                message,
                icon_type,
                show_duration
            )
            
            # Guardar en historial
            self._add_to_history(title, message, notification_type)
            
            return True
            
        except Exception as e:
            print(f"[Notification] Error showing notification: {e}")
            return False
    
    def _get_icon_type(self, notification_type: NotificationType) -> QSystemTrayIcon.MessageIcon:
        """Obtener tipo de icono según el tipo de notificación"""
        icon_map = {
            NotificationType.INFO: QSystemTrayIcon.MessageIcon.Information,
            NotificationType.SUCCESS: QSystemTrayIcon.MessageIcon.Information,
            NotificationType.WARNING: QSystemTrayIcon.MessageIcon.Warning,
            NotificationType.ERROR: QSystemTrayIcon.MessageIcon.Critical
        }
        return icon_map.get(notification_type, QSystemTrayIcon.MessageIcon.Information)
    
    def _add_to_history(self, title: str, message: str, notification_type: NotificationType):
        """Agregar notificación al historial"""
        self.notification_history.append({
            'timestamp': datetime.now(),
            'title': title,
            'message': message,
            'type': notification_type.value
        })
        
        # Mantener solo las últimas N notificaciones
        if len(self.notification_history) > self.max_history:
            self.notification_history.pop(0)
    
    def _on_notification_clicked(self):
        """Callback cuando se hace clic en una notificación"""
        if self.notification_history:
            last_notification = self.notification_history[-1]
            self.notification_clicked.emit(last_notification['title'])
    
    def get_history(self) -> list:
        """Obtener historial de notificaciones"""
        return self.notification_history.copy()
    
    def clear_history(self):
        """Limpiar historial de notificaciones"""
        self.notification_history.clear()
    
    # Métodos de conveniencia para tipos específicos
    
    def info(self, title: str, message: str, duration: int = None) -> bool:
        """Notificación informativa"""
        return self.show(title, message, NotificationType.INFO, duration)
    
    def success(self, title: str, message: str, duration: int = None) -> bool:
        """Notificación de éxito"""
        return self.show(title, message, NotificationType.SUCCESS, duration)
    
    def warning(self, title: str, message: str, duration: int = None) -> bool:
        """Notificación de advertencia"""
        return self.show(title, message, NotificationType.WARNING, duration)
    
    def error(self, title: str, message: str, duration: int = None) -> bool:
        """Notificación de error"""
        return self.show(title, message, NotificationType.ERROR, duration)
    
    # Notificaciones específicas de la aplicación
    
    def notify_mount_success(self, drive_letter: str, bucket_name: str) -> bool:
        """Notificación de montaje exitoso"""
        return self.success(
            self.tr("notify_mount_success_title"),
            self.tr("notify_mount_success_message").format(bucket_name, drive_letter)
        )
    
    def notify_mount_failed(self, drive_letter: str, error: str) -> bool:
        """Notificación de montaje fallido"""
        return self.error(
            self.tr("notify_mount_failed_title"),
            self.tr("notify_mount_failed_message").format(drive_letter, error)
        )
    
    def notify_unmount_success(self, drive_letter: str) -> bool:
        """Notificación de desmontaje exitoso"""
        return self.success(
            self.tr("notify_unmount_success_title"),
            self.tr("notify_unmount_success_message").format(drive_letter)
        )
    
    def notify_sync_complete(self, file_count: int) -> bool:
        """Notificación de sincronización completada"""
        return self.success(
            self.tr("notify_sync_complete_title"),
            self.tr("notify_sync_complete_message").format(file_count)
        )
    
    def notify_connection_lost(self) -> bool:
        """Notificación de pérdida de conexión"""
        return self.warning(
            self.tr("notify_connection_lost_title"),
            self.tr("notify_connection_lost_message")
        )
    
    def notify_connection_restored(self) -> bool:
        """Notificación de conexión restaurada"""
        return self.success(
            self.tr("notify_connection_restored_title"),
            self.tr("notify_connection_restored_message")
        )
    
    def notify_low_space(self, bucket_name: str, space_left: str) -> bool:
        """Notificación de espacio bajo"""
        return self.warning(
            self.tr("notify_low_space_title"),
            self.tr("notify_low_space_message").format(bucket_name, space_left)
        )
    
    def notify_upload_complete(self, filename: str) -> bool:
        """Notificación de carga completada"""
        return self.info(
            self.tr("notify_upload_complete_title"),
            self.tr("notify_upload_complete_message").format(filename)
        )
    
    def notify_download_complete(self, filename: str) -> bool:
        """Notificación de descarga completada"""
        return self.info(
            self.tr("notify_download_complete_title"),
            self.tr("notify_download_complete_message").format(filename)
        )
    
    def notify_app_started(self) -> bool:
        """Notificación de aplicación iniciada"""
        return self.info(
            self.tr("app_name"),
            self.tr("notify_app_started_message")
        )
    
    def notify_winfsp_installed(self) -> bool:
        """Notificación de WinFsp instalado"""
        return self.success(
            self.tr("notify_winfsp_installed_title"),
            self.tr("notify_winfsp_installed_message")
        )
    
    def notify_winfsp_install_failed(self) -> bool:
        """Notificación de instalación de WinFsp fallida"""
        return self.error(
            self.tr("notify_winfsp_failed_title"),
            self.tr("notify_winfsp_failed_message")
        )

    def tr(self, key):
        if self.translations:
            return self.translations.get(key)
        return key


# Singleton global (opcional)
_notification_manager_instance = None

def get_notification_manager(tray_icon: QSystemTrayIcon = None, translations=None) -> NotificationManager:
    """Obtener instancia global del gestor de notificaciones"""
    global _notification_manager_instance
    if _notification_manager_instance is None:
        _notification_manager_instance = NotificationManager(tray_icon, translations)
    else:
        if tray_icon is not None:
            _notification_manager_instance.set_tray_icon(tray_icon)
        if translations is not None:
            _notification_manager_instance.translations = translations
    return _notification_manager_instance


