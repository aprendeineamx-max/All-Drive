import json
import os
import sys

# ===== MEJORA #36: Encriptación de Credenciales =====
try:
    from encryption_manager import get_encryption_manager, EncryptionError
    ENCRYPTION_AVAILABLE = True
except ImportError:
    ENCRYPTION_AVAILABLE = False
    print("[ConfigManager] Advertencia: encryption_manager no disponible. Credenciales se guardarán en texto plano.")

class ConfigManager:
    def __init__(self, config_file='config.json', enable_encryption=False):
        # ===== DESHABILITAR ENCRIPTACIÓN: Credenciales en texto plano para portabilidad =====
        # Detectar si estamos ejecutando desde PyInstaller
        if getattr(sys, 'frozen', False):
            # Ejecutando desde ejecutable empaquetado
            base_path = os.path.dirname(sys.executable)
        else:
            # Ejecutando desde script Python
            base_path = os.path.dirname(os.path.abspath(__file__))
        
        self.config_file = os.path.join(base_path, config_file)
        
        # ===== ENCRIPTACIÓN DESHABILITADA: Siempre usar texto plano =====
        self.encryption_enabled = False  # Forzar deshabilitado
        self.encryption_manager = None
        
        self.configs = self.load_configs()

    def load_configs(self):
        """Cargar configuraciones y desencriptar credenciales"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    configs = json.load(f)
                
                # ===== SIN ENCRIPTACIÓN: Decodificar base64 y guardar en texto plano =====
                # Decodificar credenciales de base64 a texto plano para portabilidad
                if configs:
                    import base64
                    needs_save = False
                    
                    for profile_name, profile_data in configs.items():
                        if isinstance(profile_data, dict):
                            # Decodificar access_key si está en base64
                            if 'access_key' in profile_data and profile_data['access_key']:
                                access_key = profile_data['access_key']
                                # Si parece ser base64, decodificar
                                if len(access_key) > 50 and ('=' in access_key or access_key.replace('+', '').replace('/', '').replace('=', '').replace('-', '').replace('_', '').isalnum()):
                                    try:
                                        decoded_bytes = base64.b64decode(access_key)
                                        decoded_str = decoded_bytes.decode('utf-8', errors='ignore')
                                        
                                        # Si es un token Fernet (gAAAAA), simplemente ignorarlo
                                        # No hacer nada, dejar que el usuario reingrese las credenciales manualmente
                                        if decoded_str.startswith('gAAAAA'):
                                            # Token Fernet - no se puede usar, dejar vacío
                                            profile_data['access_key'] = ''
                                            needs_save = True
                                        elif not (decoded_str.startswith('Z0FB') or decoded_str.startswith('gAAAAA')):
                                            # Es texto plano válido después de decodificar
                                            if access_key != decoded_str:
                                                profile_data['access_key'] = decoded_str
                                                needs_save = True
                                    except Exception as e:
                                        print(f"[ConfigManager] No se pudo decodificar access_key: {e}")
                            
                            # Decodificar secret_key si está en base64
                            if 'secret_key' in profile_data and profile_data['secret_key']:
                                secret_key = profile_data['secret_key']
                                if len(secret_key) > 50 and ('=' in secret_key or secret_key.replace('+', '').replace('/', '').replace('=', '').replace('-', '').replace('_', '').isalnum()):
                                    try:
                                        decoded_bytes = base64.b64decode(secret_key)
                                        decoded_str = decoded_bytes.decode('utf-8', errors='ignore')
                                        
                                        if decoded_str.startswith('gAAAAA'):
                                            # Token Fernet - no se puede usar, dejar vacío
                                            profile_data['secret_key'] = ''
                                            needs_save = True
                                        elif not (decoded_str.startswith('Z0FB') or decoded_str.startswith('gAAAAA')):
                                            # Es texto plano válido
                                            if secret_key != decoded_str:
                                                profile_data['secret_key'] = decoded_str
                                                needs_save = True
                                    except Exception as e:
                                        print(f"[ConfigManager] No se pudo decodificar secret_key: {e}")
                    
                    # Guardar configuraciones decodificadas si hubo cambios
                    if needs_save:
                        try:
                            self.configs = configs
                            self.save_configs()
                            print(f"[ConfigManager] Credenciales decodificadas y guardadas en texto plano")
                        except Exception as e:
                            print(f"[ConfigManager] Error al guardar credenciales decodificadas: {e}")
                
                return configs
            except json.JSONDecodeError as e:
                print(f"[ConfigManager] Error al leer archivo de configuración: {e}")
                return {}
            except Exception as e:
                print(f"[ConfigManager] Error inesperado al cargar configuraciones: {e}")
                return {}
        return {}

    def save_configs(self):
        """Guardar configuraciones en texto plano (sin encriptación)"""
        try:
            # ===== SIN ENCRIPTACIÓN: Guardar credenciales en texto plano =====
            # Limpiar campos internos antes de guardar
            configs_to_save = {}
            for profile_name, profile_data in self.configs.items():
                if isinstance(profile_data, dict):
                    clean_data = {k: v for k, v in profile_data.items() 
                                 if not k.startswith('_')}  # Excluir campos internos
                    configs_to_save[profile_name] = clean_data
                else:
                    configs_to_save[profile_name] = profile_data
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(configs_to_save, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"[ConfigManager] Error al guardar configuraciones: {e}")
            raise

    def add_config(self, profile_name, access_key, secret_key, host_base):
        """
        Agregar o actualizar configuración de perfil
        
        Las credenciales se guardan en texto plano (sin encriptación) para portabilidad
        """
        self.configs[profile_name] = {
            'access_key': access_key,
            'secret_key': secret_key,
            'host_base': host_base
        }
        self.save_configs()
    
    def is_encryption_enabled(self):
        """Verificar si la encriptación está habilitada"""
        return self.encryption_enabled
    
    def migrate_to_encryption(self, force=False):
        """
        Migrar configuraciones existentes (texto plano) a encriptadas
        
        Args:
            force: Si True, forzar migración incluso si parece estar encriptado
        
        Returns:
            Número de perfiles migrados
        """
        if not self.encryption_enabled:
            return 0
        
        migrated = 0
        for profile_name, profile_data in self.configs.items():
            if isinstance(profile_data, dict):
                access_key = profile_data.get('access_key', '')
                secret_key = profile_data.get('secret_key', '')
                
                # Verificar si ya está encriptado con nuestro sistema
                is_encrypted = False
                if access_key:
                    is_encrypted = self.encryption_manager._is_encrypted(access_key)
                
                # Si no está encriptado (o forzamos), encriptar
                if force or not is_encrypted:
                    try:
                        # Verificar si realmente está encriptado intentando desencriptar
                        needs_encryption = True
                        if access_key and len(access_key) > 100:
                            try:
                                # Intentar desencriptar para verificar
                                test_decrypted = self.encryption_manager.decrypt(access_key)
                                # Si el resultado es diferente al original, ya está encriptado
                                if test_decrypted != access_key and len(test_decrypted) < len(access_key):
                                    needs_encryption = False  # Ya está encriptado correctamente
                            except Exception:
                                # No se pudo desencriptar, necesita encriptación
                                needs_encryption = True
                        
                        if needs_encryption:
                            # Si el access_key parece ser base64 pero no Fernet, 
                            # intentar decodificar primero
                            try:
                                import base64
                                # Intentar decodificar base64 para obtener el texto original
                                if access_key and '=' in access_key:
                                    try:
                                        decoded = base64.b64decode(access_key)
                                        # Si se decodifica, es base64 pero no Fernet
                                        # Usar el texto decodificado para encriptar
                                        profile_data['access_key'] = decoded.decode('utf-8', errors='ignore')
                                    except:
                                        pass  # No es base64 válido, usar tal cual
                                
                                if secret_key and '=' in secret_key:
                                    try:
                                        decoded = base64.b64decode(secret_key)
                                        profile_data['secret_key'] = decoded.decode('utf-8', errors='ignore')
                                    except:
                                        pass
                            except:
                                pass
                            
                            # Encriptar las credenciales
                            encrypted = self.encryption_manager.encrypt_dict(
                                profile_data,
                                ['access_key', 'secret_key']
                            )
                            self.configs[profile_name] = encrypted
                            migrated += 1
                    except Exception as e:
                        print(f"[ConfigManager] Error al migrar perfil '{profile_name}': {e}")
                        import traceback
                        traceback.print_exc()
        
        if migrated > 0:
            self.save_configs()
        
        return migrated

    def delete_config(self, profile_name):
        if profile_name in self.configs:
            del self.configs[profile_name]
            self.save_configs()

    def get_config(self, profile_name):
        return self.configs.get(profile_name)

    def list_profiles(self):
        """List available profiles excluding internal config keys"""
        internal_keys = {
            '_saved_mounts', 
            'active_plan', 
            'active_profile', 
            'rclone_plans', 
            'encryption_enabled'
        }
        return [k for k in self.configs.keys() if k not in internal_keys and not k.startswith('_')]

    # ===== Persistencia de montajes múltiples =====

    def save_mounts(self, mounts_data):
        """Guardar lista de montajes múltiples."""
        try:
            if not isinstance(self.configs, dict):
                self.configs = {}
            self.configs['_saved_mounts'] = mounts_data
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.configs, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"[ConfigManager] Error al guardar montajes: {e}")

    def get_saved_mounts(self):
        """Obtener montajes guardados de la configuración."""
        if not isinstance(self.configs, dict):
            return []
        return self.configs.get('_saved_mounts', [])
    
    # ===== NUEVO: Gestión de Perfiles (CRUD) =====
    
    def create_profile(self, name, access_key, secret_key, host_base):
        """
        Crear nuevo perfil de configuración.
        
        Args:
            name: Nombre único del perfil
            access_key: Vultr Access Key
            secret_key: Vultr Secret Key
            host_base: Endpoint de Object Storage (ej: sjc1.vultrobjects.com)
        
        Returns:
            (bool, str): (éxito, mensaje)
        
        Raises:
            ValueError: Si el perfil ya existe o faltan datos
        """
        # Validar datos de entrada
        if not name or not isinstance(name, str):
            raise ValueError("El nombre del perfil es obligatorio")
        
        if name in self.configs:
            raise ValueError(f"El perfil '{name}' ya existe")
        
        if not access_key or not secret_key or not host_base:
            raise ValueError("Todos los campos son obligatorios (access_key, secret_key, host_base)")
        
        # Crear perfil
        self.configs[name] = {
            'access_key': access_key.strip(),
            'secret_key': secret_key.strip(),
            'host_base': host_base.strip()
        }
        
        # Guardar cambios
        try:
            self.save_configs()
            return (True, f"Perfil '{name}' creado exitosamente")
        except Exception as e:
            # Revertir cambios si falla el guardado
            del self.configs[name]
            raise Exception(f"Error al guardar el perfil: {str(e)}")
    
    def update_profile(self, name, new_data):
        """
        Actualizar perfil existente.
        
        Args:
            name: Nombre del perfil a actualizar
            new_data: Diccionario con campos a actualizar
                     Puede contener: access_key, secret_key, host_base
        
        Returns:
            (bool, str): (éxito, mensaje)
        
        Raises:
            ValueError: Si el perfil no existe
        """
        if name not in self.configs:
            raise ValueError(f"El perfil '{name}' no existe")
        
        if not isinstance(new_data, dict):
            raise ValueError("new_data debe ser un diccionario")
        
        # Validar que solo se actualicen campos permitidos
        allowed_fields = {'access_key', 'secret_key', 'host_base'}
        invalid_fields = set(new_data.keys()) - allowed_fields
        if invalid_fields:
            raise ValueError(f"Campos no permitidos: {invalid_fields}")
        
        # Actualizar campos
        for key, value in new_data.items():
            if value:  # Solo actualizar si no está vacío
                self.configs[name][key] = value.strip() if isinstance(value, str) else value
        
        # Guardar cambios
        try:
            self.save_configs()
            return (True, f"Perfil '{name}' actualizado exitosamente")
        except Exception as e:
            raise Exception(f"Error al guardar los cambios: {str(e)}")
    
    def delete_profile(self, name):
        """
        Eliminar perfil.
        
        Args:
            name: Nombre del perfil a eliminar
        
        Returns:
            (bool, str): (éxito, mensaje)
        
        Raises:
            ValueError: Si el perfil no existe
        """
        if name not in self.configs:
            raise ValueError(f"El perfil '{name}' no existe")
        
        # Eliminar perfil
        del self.configs[name]
        
        # Guardar cambios
        try:
            self.save_configs()
            return (True, f"Perfil '{name}' eliminado exitosamente")
        except Exception as e:
            raise Exception(f"Error al guardar los cambios: {str(e)}")
    
    def validate_profile_name(self, name):
        """
        Validar que el nombre de perfil sea único.
        
        Args:
            name: Nombre del perfil a validar
        
        Returns:
            bool: True si el nombre es válido (no existe), False si ya existe
        """
        if not name or not isinstance(name, str):
            return False
        
        return name not in self.configs
    
    def get_profile_data(self, profile_name):
        """
        Obtener datos completos de un perfil.
        
        Args:
            profile_name: Nombre del perfil
        
        Returns:
            dict o None: Datos del perfil si existe, None si no existe
        """
        return self.configs.get(profile_name)

    # ===== NUEVO: Gestión de Planes Rclone (Fase 7) =====

    def get_plans(self):
        """Retorna diccionario de planes. Crea defaults si no existen."""
        if 'rclone_plans' not in self.configs:
            self.configs['rclone_plans'] = {
                "Ultra Performance 🚀": {
                    "transfers": "320",
                    "checkers": "320",
                    "tpslimit": "0",
                    "burst": "0",
                    "vfs_cache_mode": "writes",
                    "vfs_write_back": "5s",
                    "buffer_size": "64M",
                    "vfs_read_chunk_size": "128M",
                    "timeout": "10h",
                    "retries": "5"
                },
                "Balanced ⚖️": {
                    "transfers": "32",
                    "checkers": "32",
                    "tpslimit": "50",
                    "burst": "20",
                    "vfs_cache_mode": "writes",
                    "vfs_write_back": "10s",
                    "buffer_size": "32M",
                    "vfs_read_chunk_size": "64M",
                    "timeout": "1h",
                    "retries": "3"
                },
                "Stability 🛡️": {
                    "transfers": "4",
                    "checkers": "8",
                    "tpslimit": "10",
                    "burst": "5",
                    "vfs_cache_mode": "full",
                    "vfs_write_back": "1m",
                    "buffer_size": "16M",
                    "vfs_read_chunk_size": "32M",
                    "timeout": "30m",
                    "retries": "10"
                }
            }
            # Set active if not exists
            if 'active_plan' not in self.configs:
                self.configs['active_plan'] = "Ultra Performance 🚀"
            
            self.save_configs()
            
        return self.configs['rclone_plans']

    def get_plan(self, name):
        plans = self.get_plans()
        return plans.get(name)

    def save_plan(self, name, plan_config):
        self.get_plans() # Ensure exists
        self.configs['rclone_plans'][name] = plan_config
        self.save_configs()

    def delete_plan(self, name):
        if 'rclone_plans' in self.configs and name in self.configs['rclone_plans']:
            del self.configs['rclone_plans'][name]
            self.save_configs()

    def get_active_plan(self):
        self.get_plans() # Ensure initialization
        return self.configs.get('active_plan', "Ultra Performance 🚀")

    def set_active_plan(self, name):
        self.configs['active_plan'] = name
        self.save_configs()

    def get_active_profile(self):
        """Retorna el nombre del perfil activo o None."""
        return self.configs.get('active_profile')

    def set_active_profile(self, name):
        """Guarda el perfil activo."""
        self.configs['active_profile'] = name
        self.save_configs()

    # ===== Configuración de GCP Sync =====
    
    def get_gcp_sync_config(self):
        """Obtener configuración guardada de sincronización GCP"""
        return self.configs.get('_gcp_sync', {})

    def set_gcp_sync_config(self, config):
        """Guardar configuración de sincronización GCP"""
        self.configs['_gcp_sync'] = config
        self.save_configs()
