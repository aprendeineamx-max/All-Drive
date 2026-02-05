"""
Base Storage - Clase abstracta para tipos de almacenamiento

Todos los tipos de almacenamiento (Vultr S3, MEGA, Google Drive, etc.)
deben heredar de esta clase e implementar sus métodos.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from PyQt6.QtWidgets import QWidget


@dataclass
class StorageAccount:
    """Representa una cuenta de almacenamiento configurada"""
    id: str                 # Identificador único
    name: str               # Nombre para mostrar
    storage_type: str       # "vultr_s3", "mega", "gdrive", etc.
    config: Dict[str, Any]  # Configuración específica del tipo
    
    def __str__(self):
        return f"{self.name} ({self.storage_type})"


@dataclass
class StorageItem:
    """Representa un elemento en el almacenamiento (archivo o carpeta)"""
    name: str
    path: str
    is_dir: bool
    size: int = 0
    modified: Optional[str] = None


class BaseStorage(ABC):
    """
    Clase base abstracta para todos los tipos de almacenamiento.
    
    Cada implementación debe proporcionar:
    - Icono y colores para la UI
    - Métodos para gestionar cuentas
    - Métodos para operaciones de archivos
    - Pestañas específicas del tipo
    """
    
    # Propiedades de UI (deben ser sobrescritas)
    name: str = "Unknown Storage"
    icon: str = "📁"
    color: str = "#888888"
    description: str = "Tipo de almacenamiento genérico"
    
    def __init__(self, config_manager, rclone_manager):
        """
        Inicializa el tipo de almacenamiento.
        
        Args:
            config_manager: Gestor de configuración de la app
            rclone_manager: Gestor de rclone para montaje
        """
        self.config_manager = config_manager
        self.rclone_manager = rclone_manager
    
    # ===== MÉTODOS DE CUENTAS =====
    
    @abstractmethod
    def get_accounts(self) -> List[StorageAccount]:
        """
        Obtiene todas las cuentas configuradas de este tipo.
        
        Returns:
            Lista de StorageAccount
        """
        pass
    
    @abstractmethod
    def add_account(self, **kwargs) -> Tuple[bool, str]:
        """
        Agrega una nueva cuenta.
        
        Args:
            **kwargs: Parámetros específicos del tipo (user, password, api_key, etc.)
        
        Returns:
            Tuple (éxito: bool, mensaje: str)
        """
        pass
    
    @abstractmethod
    def remove_account(self, account_id: str) -> Tuple[bool, str]:
        """
        Elimina una cuenta existente.
        
        Args:
            account_id: ID de la cuenta a eliminar
        
        Returns:
            Tuple (éxito: bool, mensaje: str)
        """
        pass
    
    @abstractmethod
    def validate_account(self, account: StorageAccount) -> Tuple[bool, str]:
        """
        Valida que las credenciales de una cuenta sean correctas.
        
        Args:
            account: Cuenta a validar
        
        Returns:
            Tuple (válida: bool, mensaje: str)
        """
        pass
    
    # ===== MÉTODOS DE MONTAJE =====
    
    @abstractmethod
    def mount(self, account: StorageAccount, drive_letter: str, 
              path: str = "/", **options) -> Tuple[bool, str, Any]:
        """
        Monta el almacenamiento como unidad local.
        
        Args:
            account: Cuenta a montar
            drive_letter: Letra de unidad (ej: "V")
            path: Ruta dentro del almacenamiento (default: raíz)
            **options: Opciones adicionales de montaje
        
        Returns:
            Tuple (éxito: bool, mensaje: str, proceso: Any)
        """
        pass
    
    @abstractmethod
    def unmount(self, drive_letter: str) -> Tuple[bool, str]:
        """
        Desmonta una unidad.
        
        Args:
            drive_letter: Letra de unidad a desmontar
        
        Returns:
            Tuple (éxito: bool, mensaje: str)
        """
        pass
    
    # ===== MÉTODOS DE ARCHIVOS =====
    
    @abstractmethod
    def list_contents(self, account: StorageAccount, 
                      path: str = "/") -> Tuple[List[StorageItem], str]:
        """
        Lista el contenido de una ruta.
        
        Args:
            account: Cuenta a usar
            path: Ruta a listar
        
        Returns:
            Tuple (items: List[StorageItem], error: str o vacío)
        """
        pass
    
    @abstractmethod
    def upload_file(self, account: StorageAccount, 
                    local_path: str, remote_path: str) -> Tuple[bool, str]:
        """
        Sube un archivo al almacenamiento.
        
        Args:
            account: Cuenta destino
            local_path: Ruta local del archivo
            remote_path: Ruta destino en el almacenamiento
        
        Returns:
            Tuple (éxito: bool, mensaje: str)
        """
        pass
    
    @abstractmethod
    def upload_folder(self, account: StorageAccount, 
                      local_path: str, remote_path: str) -> Tuple[bool, str]:
        """
        Sube una carpeta completa al almacenamiento.
        
        Args:
            account: Cuenta destino
            local_path: Ruta local de la carpeta
            remote_path: Ruta destino en el almacenamiento
        
        Returns:
            Tuple (éxito: bool, mensaje: str)
        """
        pass
    
    # ===== MÉTODOS DE UI =====
    
    @abstractmethod
    def get_account_form_fields(self) -> List[Dict[str, Any]]:
        """
        Retorna la definición de campos para el formulario de agregar cuenta.
        
        Returns:
            Lista de diccionarios con:
            - name: nombre del campo
            - label: etiqueta para mostrar
            - type: "text", "password", "select"
            - placeholder: texto de ayuda
            - required: bool
            - options: lista de opciones (solo para type="select")
        """
        pass
    
    def get_tabs(self) -> List[QWidget]:
        """
        Retorna las pestañas específicas de este tipo de almacenamiento.
        
        Override este método para agregar pestañas personalizadas.
        Por defecto retorna una lista vacía (usa las pestañas compartidas).
        
        Returns:
            Lista de QWidget para agregar como pestañas
        """
        return []
    
    # ===== MÉTODOS DE UTILIDAD =====
    
    def get_display_info(self) -> Dict[str, str]:
        """
        Retorna información para mostrar en la UI.
        
        Returns:
            Dict con name, icon, color, description
        """
        return {
            "name": self.name,
            "icon": self.icon,
            "color": self.color,
            "description": self.description
        }
    
    def supports_buckets(self) -> bool:
        """
        Indica si este tipo usa concepto de buckets (como S3).
        Override para cambiar el comportamiento.
        
        Returns:
            True si usa buckets, False si usa carpetas directamente
        """
        return False
    
    def supports_sync(self) -> bool:
        """
        Indica si este tipo soporta sincronización en tiempo real.
        
        Returns:
            True si soporta sync, False si no
        """
        return True
