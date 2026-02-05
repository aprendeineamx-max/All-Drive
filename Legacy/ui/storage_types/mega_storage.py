"""
MEGA Storage - Implementación para almacenamiento MEGA.nz
"""

from typing import List, Dict, Any, Tuple
from .base_storage import BaseStorage, StorageAccount, StorageItem


class MegaStorage(BaseStorage):
    """
    Implementación de almacenamiento para MEGA.nz usando rclone.
    """
    
    name = "MEGA.nz"
    icon = "☁️"
    color = "#e74c3c"
    description = "Almacenamiento en la nube de MEGA (50GB gratis)"
    
    def __init__(self, config_manager, rclone_manager):
        super().__init__(config_manager, rclone_manager)
    
    def get_accounts(self) -> List[StorageAccount]:
        """Obtiene todas las cuentas MEGA configuradas"""
        accounts = []
        mega_profiles = self.rclone_manager.list_mega_profiles()
        
        for profile in mega_profiles:
            accounts.append(StorageAccount(
                id=profile['name'],
                name=profile['name'],
                storage_type="mega",
                config={"user": profile['user']}
            ))
        
        return accounts
    
    def add_account(self, name: str, user: str, password: str) -> Tuple[bool, str]:
        """Agrega una nueva cuenta MEGA"""
        # Validar nombre sin espacios
        if " " in name:
            return False, "El nombre no debe contener espacios"
        
        success, message = self.rclone_manager.create_mega_config(name, user, password)
        return success, message
    
    def remove_account(self, account_id: str) -> Tuple[bool, str]:
        """Elimina una cuenta MEGA"""
        success, message = self.rclone_manager.delete_rclone_profile(account_id)
        return success, message
    
    def validate_account(self, account: StorageAccount) -> Tuple[bool, str]:
        """Valida las credenciales de una cuenta MEGA"""
        try:
            items, error = self.list_contents(account, "/")
            if error:
                return False, error
            return True, f"Cuenta válida. {len(items)} elemento(s) en raíz."
        except Exception as e:
            return False, f"Error de validación: {str(e)}"
    
    def mount(self, account: StorageAccount, drive_letter: str,
              path: str = "/", **options) -> Tuple[bool, str, Any]:
        """Monta MEGA como unidad local"""
        plan_config = options.get('plan_config')
        
        # Para MEGA, el "bucket" es la ruta (/ para raíz)
        success, message, process = self.rclone_manager.mount_drive(
            account.id,
            drive_letter,
            bucket_name=None,  # MEGA no usa buckets
            plan_config=plan_config
        )
        
        return success, message, process
    
    def unmount(self, drive_letter: str) -> Tuple[bool, str]:
        """Desmonta una unidad"""
        success, message = self.rclone_manager.unmount_drive(drive_letter)
        return success, message
    
    def list_contents(self, account: StorageAccount,
                      path: str = "/") -> Tuple[List[StorageItem], str]:
        """Lista el contenido de una ruta en MEGA"""
        try:
            # Usar rclone lsd para listar directorios
            import subprocess
            import sys
            
            rclone_path = self.rclone_manager._find_rclone_executable()
            if not rclone_path:
                return [], "Rclone no encontrado"
            
            cmd = [
                rclone_path,
                "lsjson",
                f"{account.id}:{path}",
                "--config", self.rclone_manager.rclone_config_file
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
            )
            
            if result.returncode != 0:
                return [], result.stderr
            
            import json
            data = json.loads(result.stdout) if result.stdout.strip() else []
            
            items = []
            for item in data:
                items.append(StorageItem(
                    name=item.get('Name', ''),
                    path=f"{path.rstrip('/')}/{item.get('Path', '')}",
                    is_dir=item.get('IsDir', False),
                    size=item.get('Size', 0),
                    modified=item.get('ModTime', '')
                ))
            
            return items, ""
        except Exception as e:
            return [], str(e)
    
    def upload_file(self, account: StorageAccount,
                    local_path: str, remote_path: str) -> Tuple[bool, str]:
        """Sube un archivo a MEGA"""
        return self.rclone_manager.copy_file_to_remote(
            account.id, local_path, remote_path
        )
    
    def upload_folder(self, account: StorageAccount,
                      local_path: str, remote_path: str) -> Tuple[bool, str]:
        """Sube una carpeta completa a MEGA"""
        return self.rclone_manager.copy_folder_to_remote(
            account.id, local_path, remote_path
        )
    
    def get_account_form_fields(self) -> List[Dict[str, Any]]:
        """Retorna los campos para el formulario de nueva cuenta MEGA"""
        return [
            {
                "name": "name",
                "label": "Nombre del Perfil",
                "type": "text",
                "placeholder": "Ej: MiMegaPersonal",
                "required": True
            },
            {
                "name": "user",
                "label": "Correo Electrónico",
                "type": "text",
                "placeholder": "correo@ejemplo.com",
                "required": True
            },
            {
                "name": "password",
                "label": "Contraseña",
                "type": "password",
                "placeholder": "Tu contraseña de MEGA",
                "required": True
            }
        ]
    
    def supports_buckets(self) -> bool:
        """MEGA no usa buckets, usa carpetas directamente"""
        return False
