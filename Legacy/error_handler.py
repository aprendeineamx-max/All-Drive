"""
Sistema de Manejo de Errores Mejorado - VultrDrive Desktop
Mejora #48: Excepciones específicas, mensajes descriptivos y recovery automático
"""

from enum import Enum
from typing import Optional, Callable, Dict, Any
import traceback

# ===== MEJORA #47: Integración con logging =====
try:
    from logger_manager import get_logger
    logger = get_logger("ErrorHandler")
    LOGGING_AVAILABLE = True
except ImportError:
    LOGGING_AVAILABLE = False
    logger = None


class ErrorCategory(Enum):
    """Categorías de errores"""
    CONNECTION = "Conexión"
    AUTHENTICATION = "Autenticación"
    CONFIGURATION = "Configuración"
    FILE_OPERATION = "Operación de Archivo"
    MOUNT_OPERATION = "Operación de Montaje"
    NETWORK = "Red"
    PERMISSION = "Permisos"
    RESOURCE = "Recursos"
    UNKNOWN = "Desconocido"


class VultrDriveError(Exception):
    """Excepción base para todos los errores de VultrDrive"""
    
    def __init__(self, message: str, category: ErrorCategory = ErrorCategory.UNKNOWN, 
                 suggestion: Optional[str] = None, recoverable: bool = False,
                 original_error: Optional[Exception] = None):
        """
        Inicializar excepción personalizada
        
        Args:
            message: Mensaje de error descriptivo
            category: Categoría del error
            suggestion: Sugerencia de solución (opcional)
            recoverable: Si el error es recuperable automáticamente
            original_error: Error original que causó este error
        """
        super().__init__(message)
        self.message = message
        self.category = category
        self.suggestion = suggestion
        self.recoverable = recoverable
        self.original_error = original_error
        self.traceback = traceback.format_exc() if original_error else None
    
    def get_user_message(self) -> str:
        """Obtener mensaje formateado para el usuario"""
        msg = f"❌ {self.category.value}: {self.message}"
        if self.suggestion:
            msg += f"\n\n💡 Sugerencia: {self.suggestion}"
        return msg
    
    def __str__(self):
        return self.get_user_message()


class ConnectionError(VultrDriveError):
    """Error de conexión con el servidor"""
    
    def __init__(self, message: str = "No se pudo conectar con el servidor", 
                 suggestion: Optional[str] = None, original_error: Optional[Exception] = None):
        if suggestion is None:
            suggestion = (
                "1. Verifica tu conexión a internet\n"
                "2. Verifica que el endpoint de Vultr sea correcto\n"
                "3. Intenta nuevamente en unos momentos"
            )
        super().__init__(message, ErrorCategory.CONNECTION, suggestion, 
                        recoverable=True, original_error=original_error)


class AuthenticationError(VultrDriveError):
    """Error de autenticación"""
    
    def __init__(self, message: str = "Credenciales inválidas", 
                 suggestion: Optional[str] = None, original_error: Optional[Exception] = None):
        if suggestion is None:
            suggestion = (
                "1. Verifica tu Access Key y Secret Key\n"
                "2. Asegúrate de que las credenciales sean correctas\n"
                "3. Verifica que la cuenta no esté bloqueada"
            )
        super().__init__(message, ErrorCategory.AUTHENTICATION, suggestion, 
                        recoverable=False, original_error=original_error)


class ConfigurationError(VultrDriveError):
    """Error de configuración"""
    
    def __init__(self, message: str = "Error en la configuración", 
                 suggestion: Optional[str] = None, original_error: Optional[Exception] = None):
        if suggestion is None:
            suggestion = (
                "1. Verifica que todos los campos estén completos\n"
                "2. Revisa la configuración en la pestaña de Configuración\n"
                "3. Intenta eliminar y recrear el perfil"
            )
        super().__init__(message, ErrorCategory.CONFIGURATION, suggestion, 
                        recoverable=False, original_error=original_error)


class MountError(VultrDriveError):
    """Error al montar/desmontar unidad"""
    
    def __init__(self, message: str = "Error al montar la unidad", 
                 suggestion: Optional[str] = None, original_error: Optional[Exception] = None):
        if suggestion is None:
            suggestion = (
                "1. Verifica que WinFsp esté instalado correctamente\n"
                "2. Asegúrate de que la letra de unidad no esté en uso\n"
                "3. Reinicia la aplicación e intenta nuevamente"
            )
        super().__init__(message, ErrorCategory.MOUNT_OPERATION, suggestion, 
                        recoverable=True, original_error=original_error)


class FileOperationError(VultrDriveError):
    """Error en operación de archivo"""
    
    def __init__(self, message: str = "Error en operación de archivo", 
                 suggestion: Optional[str] = None, original_error: Optional[Exception] = None):
        if suggestion is None:
            suggestion = (
                "1. Verifica que el archivo no esté en uso\n"
                "2. Asegúrate de tener permisos de lectura/escritura\n"
                "3. Verifica que haya espacio disponible"
            )
        super().__init__(message, ErrorCategory.FILE_OPERATION, suggestion, 
                        recoverable=True, original_error=original_error)


class NetworkError(VultrDriveError):
    """Error de red"""
    
    def __init__(self, message: str = "Error de red", 
                 suggestion: Optional[str] = None, original_error: Optional[Exception] = None):
        if suggestion is None:
            suggestion = (
                "1. Verifica tu conexión a internet\n"
                "2. Revisa tu firewall y antivirus\n"
                "3. Intenta nuevamente en unos momentos"
            )
        super().__init__(message, ErrorCategory.NETWORK, suggestion, 
                        recoverable=True, original_error=original_error)


class PermissionError(VultrDriveError):
    """Error de permisos"""
    
    def __init__(self, message: str = "Permisos insuficientes", 
                 suggestion: Optional[str] = None, original_error: Optional[Exception] = None):
        if suggestion is None:
            suggestion = (
                "1. Ejecuta la aplicación como administrador\n"
                "2. Verifica los permisos de la carpeta\n"
                "3. Revisa la configuración de seguridad de Windows"
            )
        super().__init__(message, ErrorCategory.PERMISSION, suggestion, 
                        recoverable=False, original_error=original_error)


class ResourceError(VultrDriveError):
    """Error de recursos (espacio, memoria, etc.)"""
    
    def __init__(self, message: str = "Recurso no disponible", 
                 suggestion: Optional[str] = None, original_error: Optional[Exception] = None):
        if suggestion is None:
            suggestion = (
                "1. Libera espacio en disco\n"
                "2. Cierra otras aplicaciones que usen muchos recursos\n"
                "3. Reinicia la aplicación"
            )
        super().__init__(message, ErrorCategory.RESOURCE, suggestion, 
                        recoverable=True, original_error=original_error)


class ErrorHandler:
    """
    Gestor centralizado de errores
    
    Proporciona:
    - Captura y clasificación de errores
    - Mensajes descriptivos para el usuario
    - Sugerencias de solución
    - Recovery automático cuando sea posible
    - Logging de errores
    """
    
    def __init__(self):
        self.recovery_handlers: Dict[ErrorCategory, Callable] = {}
        self.error_count: Dict[ErrorCategory, int] = {}
    
    def register_recovery_handler(self, category: ErrorCategory, handler: Callable):
        """
        Registrar handler de recovery para una categoría
        
        Args:
            category: Categoría de error
            handler: Función que intenta recuperar del error
        """
        self.recovery_handlers[category] = handler
    
    def handle_error(self, error: Exception, context: Optional[str] = None) -> VultrDriveError:
        """
        Manejar un error y convertirlo en VultrDriveError
        
        Args:
            error: Excepción original
            context: Contexto adicional del error
            
        Returns:
            VultrDriveError apropiado
        """
        # Si ya es un VultrDriveError, retornarlo
        if isinstance(error, VultrDriveError):
            self._log_error(error, context)
            return error
        
        # Clasificar el error
        vultr_error = self._classify_error(error, context)
        
        # Contar errores
        self.error_count[vultr_error.category] = self.error_count.get(vultr_error.category, 0) + 1
        
        # Logging
        self._log_error(vultr_error, context)
        
        return vultr_error
    
    def _classify_error(self, error: Exception, context: Optional[str] = None) -> VultrDriveError:
        """Clasificar error y crear VultrDriveError apropiado"""
        error_str = str(error).lower()
        error_type = type(error).__name__
        
        # Errores de conexión
        if any(keyword in error_str for keyword in ['connection', 'connect', 'timeout', 'unreachable']):
            return ConnectionError(
                f"Error de conexión: {str(error)}",
                original_error=error
            )
        
        # Errores de autenticación
        if any(keyword in error_str for keyword in ['auth', 'credential', 'unauthorized', 'forbidden', '403', '401']):
            return AuthenticationError(
                f"Error de autenticación: {str(error)}",
                original_error=error
            )
        
        # Errores de montaje
        if any(keyword in error_str for keyword in ['mount', 'unmount', 'winfsp', 'rclone']):
            suggestion = self._get_mount_suggestion(error_str)
            return MountError(
                f"Error al montar: {str(error)}",
                suggestion=suggestion,
                original_error=error
            )
        
        # Errores de archivo
        if any(keyword in error_str for keyword in ['file', 'directory', 'path', 'not found', 'permission denied']):
            return FileOperationError(
                f"Error de archivo: {str(error)}",
                original_error=error
            )
        
        # Errores de red
        if any(keyword in error_str for keyword in ['network', 'dns', 'resolve', 'socket']):
            return NetworkError(
                f"Error de red: {str(error)}",
                original_error=error
            )
        
        # Errores de permisos
        if any(keyword in error_str for keyword in ['permission', 'access denied', 'unauthorized']):
            return PermissionError(
                f"Error de permisos: {str(error)}",
                original_error=error
            )
        
        # Error genérico
        return VultrDriveError(
            f"Error: {str(error)}",
            category=ErrorCategory.UNKNOWN,
            suggestion="Por favor, reporta este error al soporte técnico.",
            original_error=error
        )
    
    def _get_mount_suggestion(self, error_str: str) -> str:
        """Obtener sugerencia específica para errores de montaje"""
        if 'winfsp' in error_str:
            return (
                "1. Verifica que WinFsp esté instalado correctamente\n"
                "2. Reinicia Windows después de instalar WinFsp\n"
                "3. Ejecuta la aplicación como administrador"
            )
        elif 'already' in error_str or 'en uso' in error_str:
            return (
                "1. La letra de unidad ya está en uso\n"
                "2. Selecciona otra letra (W:, X:, Y:, Z:)\n"
                "3. O desmonta la unidad existente primero"
            )
        else:
            return (
                "1. Verifica que WinFsp esté instalado\n"
                "2. Asegúrate de que la letra de unidad no esté en uso\n"
                "3. Verifica tus credenciales de Vultr"
            )
    
    def _log_error(self, error: VultrDriveError, context: Optional[str] = None):
        """Registrar error en el log"""
        if LOGGING_AVAILABLE and logger:
            log_msg = f"[{error.category.value}] {error.message}"
            if context:
                log_msg += f" | Contexto: {context}"
            
            if error.original_error:
                logger.exception(log_msg, exc_info=error.original_error)
            else:
                logger.error(log_msg)
            
            if error.suggestion:
                logger.info(f"Sugerencia: {error.suggestion}")
    
    def try_recover(self, error: VultrDriveError, *args, **kwargs) -> tuple[bool, Optional[str]]:
        """
        Intentar recuperar automáticamente de un error
        
        Args:
            error: Error a recuperar
            *args, **kwargs: Argumentos para el handler de recovery
            
        Returns:
            (success, message) - True si se recuperó, False si no
        """
        if not error.recoverable:
            return False, "Este error no es recuperable automáticamente"
        
        handler = self.recovery_handlers.get(error.category)
        if not handler:
            return False, "No hay handler de recovery para este tipo de error"
        
        try:
            result = handler(*args, **kwargs)
            if result:
                if LOGGING_AVAILABLE and logger:
                    logger.info(f"Recovery exitoso para error: {error.category.value}")
                return True, "Error recuperado automáticamente"
            else:
                return False, "Recovery falló"
        except Exception as e:
            if LOGGING_AVAILABLE and logger:
                logger.error(f"Error en recovery handler: {e}")
            return False, f"Error en recovery: {str(e)}"
    
    def get_error_stats(self) -> Dict[str, int]:
        """Obtener estadísticas de errores"""
        return {cat.value: count for cat, count in self.error_count.items()}
    
    def reset_stats(self):
        """Resetear estadísticas de errores"""
        self.error_count.clear()


# Singleton global
_error_handler_instance = None

def get_error_handler() -> ErrorHandler:
    """Obtener instancia global del gestor de errores"""
    global _error_handler_instance
    if _error_handler_instance is None:
        _error_handler_instance = ErrorHandler()
    return _error_handler_instance

def handle_error(error: Exception, context: Optional[str] = None) -> VultrDriveError:
    """
    Función de conveniencia para manejar errores
    
    Args:
        error: Excepción a manejar
        context: Contexto adicional
        
    Returns:
        VultrDriveError
    """
    handler = get_error_handler()
    return handler.handle_error(error, context)

