"""
Vultr S3 Storage - Implementación para almacenamiento Vultr Object Storage (S3)
"""

from typing import List, Dict, Any, Tuple
from .base_storage import BaseStorage, StorageAccount, StorageItem


class VultrS3Storage(BaseStorage):
    """
    Implementación de almacenamiento para Vultr Object Storage (S3 compatible).
    """
    
    name = "Vultr S3"
    icon = "🔷"
    color = "#3498db"
    description = "Almacenamiento de objetos compatible con S3 de Vultr"
    
    def __init__(self, config_manager, rclone_manager):
        super().__init__(config_manager, rclone_manager)
        self._s3_handlers = {}  # Cache de handlers S3 por cuenta
    
    def get_accounts(self) -> List[StorageAccount]:
        """Obtiene todas las cuentas Vultr S3 configuradas"""
        accounts = []
        profiles = self.config_manager.list_profiles()
        
        for profile_name in profiles:
            config = self.config_manager.get_config(profile_name)
            if config and isinstance(config, dict):
                # Solo incluir si tiene las claves de S3
                if 'access_key' in config and 'secret_key' in config:
                    accounts.append(StorageAccount(
                        id=profile_name,
                        name=profile_name,
                        storage_type="vultr_s3",
                        config=config
                    ))
        
        return accounts
    
    def add_account(self, name: str, access_key: str, 
                    secret_key: str, host_base: str) -> Tuple[bool, str]:
        """Agrega una nueva cuenta Vultr S3"""
        try:
            self.config_manager.create_profile(name, access_key, secret_key, host_base)
            return True, f"Cuenta '{name}' creada exitosamente"
        except ValueError as e:
            return False, str(e)
        except Exception as e:
            return False, f"Error al crear cuenta: {str(e)}"
    
    def remove_account(self, account_id: str) -> Tuple[bool, str]:
        """Elimina una cuenta Vultr S3"""
        try:
            self.config_manager.delete_profile(account_id)
            if account_id in self._s3_handlers:
                del self._s3_handlers[account_id]
            return True, f"Cuenta '{account_id}' eliminada"
        except ValueError as e:
            return False, str(e)
        except Exception as e:
            return False, f"Error al eliminar: {str(e)}"
    
    def validate_account(self, account: StorageAccount) -> Tuple[bool, str]:
        """Valida las credenciales de una cuenta Vultr S3"""
        try:
            handler = self._get_s3_handler(account)
            buckets, error = handler.list_buckets()
            if error:
                return False, error
            return True, f"Cuenta válida. {len(buckets)} bucket(s) encontrado(s)."
        except Exception as e:
            return False, f"Error de validación: {str(e)}"
    
    def mount(self, account: StorageAccount, drive_letter: str,
              path: str = "/", **options) -> Tuple[bool, str, Any]:
        """Monta un bucket de Vultr S3 como unidad local"""
        bucket_name = options.get('bucket_name')
        plan_config = options.get('plan_config')
        
        if not bucket_name:
            return False, "Se requiere especificar un bucket", None
        
        success, message, process = self.rclone_manager.mount_drive(
            account.id, 
            drive_letter, 
            bucket_name, 
            plan_config
        )
        
        return success, message, process
    
    def unmount(self, drive_letter: str) -> Tuple[bool, str]:
        """Desmonta una unidad"""
        success, message = self.rclone_manager.unmount_drive(drive_letter)
        return success, message
    
    def list_contents(self, account: StorageAccount,
                      path: str = "/") -> Tuple[List[StorageItem], str]:
        """Lista el contenido de un bucket o ruta"""
        # Para S3, path debería ser "bucket_name" o "bucket_name/folder"
        try:
            buckets = self.rclone_manager.list_buckets_rclone(account.id)
            items = [
                StorageItem(name=b, path=f"/{b}", is_dir=True)
                for b in buckets
            ]
            return items, ""
        except Exception as e:
            return [], str(e)
    
    def upload_file(self, account: StorageAccount,
                    local_path: str, remote_path: str) -> Tuple[bool, str]:
        """Sube un archivo a Vultr S3"""
        try:
            handler = self._get_s3_handler(account)
            # Extraer bucket del remote_path
            parts = remote_path.strip('/').split('/', 1)
            bucket = parts[0]
            key = parts[1] if len(parts) > 1 else ""
            
            import os
            file_name = os.path.basename(local_path)
            full_key = f"{key}/{file_name}" if key else file_name
            
            handler.upload_file(local_path, bucket, full_key)
            return True, f"Archivo subido a {bucket}/{full_key}"
        except Exception as e:
            return False, str(e)
    
    def upload_folder(self, account: StorageAccount,
                      local_path: str, remote_path: str) -> Tuple[bool, str]:
        """Sube una carpeta completa a Vultr S3"""
        try:
            handler = self._get_s3_handler(account)
            parts = remote_path.strip('/').split('/', 1)
            bucket = parts[0]
            prefix = parts[1] if len(parts) > 1 else ""
            
            # Usar el backup_folder del handler
            handler.backup_folder(local_path, bucket, prefix)
            return True, f"Carpeta respaldada a {bucket}"
        except Exception as e:
            return False, str(e)
    
    def get_account_form_fields(self) -> List[Dict[str, Any]]:
        """Retorna los campos para el formulario de nueva cuenta"""
        return [
            {
                "name": "name",
                "label": "Nombre del Perfil",
                "type": "text",
                "placeholder": "Ej: mi-vultr-principal",
                "required": True
            },
            {
                "name": "access_key",
                "label": "Access Key",
                "type": "text",
                "placeholder": "Ej: VVQQYYLLLHH4OB6ZZAABBC",
                "required": True
            },
            {
                "name": "secret_key",
                "label": "Secret Key",
                "type": "password",
                "placeholder": "Tu clave secreta de Vultr",
                "required": True
            },
            {
                "name": "host_base",
                "label": "Región/Endpoint",
                "type": "select",
                "required": True,
                "options": [
                    {"value": "ewr1.vultrobjects.com", "label": "🇺🇸 New Jersey (ewr1)"},
                    {"value": "sjc1.vultrobjects.com", "label": "🇺🇸 Silicon Valley (sjc1)"},
                    {"value": "lax1.vultrobjects.com", "label": "🇺🇸 Los Angeles (lax1)"},
                    {"value": "ams1.vultrobjects.com", "label": "🇳🇱 Amsterdam (ams1)"},
                    {"value": "sgp1.vultrobjects.com", "label": "🇸🇬 Singapore (sgp1)"},
                    {"value": "blr1.vultrobjects.com", "label": "🇮🇳 Bangalore (blr1)"},
                ]
            }
        ]
    
    def supports_buckets(self) -> bool:
        """Vultr S3 usa buckets"""
        return True
    
    def get_buckets(self, account: StorageAccount) -> Tuple[List[str], str]:
        """Obtiene la lista de buckets de una cuenta"""
        try:
            buckets = self.rclone_manager.list_buckets_rclone(account.id)
            return buckets, ""
        except Exception as e:
            return [], str(e)
    
    def _get_s3_handler(self, account: StorageAccount):
        """Obtiene o crea un handler S3 para la cuenta"""
        if account.id not in self._s3_handlers:
            from s3_handler import S3Handler
            self._s3_handlers[account.id] = S3Handler(
                account.config.get('access_key'),
                account.config.get('secret_key'),
                account.config.get('host_base')
            )
        return self._s3_handlers[account.id]
