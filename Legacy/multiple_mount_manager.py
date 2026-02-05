"""
Gestor de Múltiples Montajes - VultrDrive Desktop
Permite montar múltiples buckets simultáneamente en diferentes letras de unidad
"""

import subprocess
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple

class MountInfo:
    """Información de un montaje individual"""
    def __init__(self, letter: str, profile: str, bucket: str, process=None):
        self.letter = letter
        self.profile = profile
        self.bucket = bucket
        self.process = process
        self.status = 'mounting'  # mounting, connected, disconnected, error
        self.mounted_at = datetime.now()
        self.error_message = None
        
    def to_dict(self):
        """Convertir a diccionario para persistencia"""
        return {
            'letter': self.letter,
            'profile': self.profile,
            'bucket': self.bucket,
            'status': self.status,
            'mounted_at': self.mounted_at.isoformat() if self.mounted_at else None,
            'error_message': self.error_message
        }
    
    @staticmethod
    def from_dict(data: dict):
        """Crear desde diccionario"""
        mount_info = MountInfo(
            data['letter'],
            data['profile'],
            data['bucket']
        )
        mount_info.status = data.get('status', 'disconnected')
        if data.get('mounted_at'):
            mount_info.mounted_at = datetime.fromisoformat(data['mounted_at'])
        mount_info.error_message = data.get('error_message')
        return mount_info


class MultipleMountManager:
    """
    Gestor de múltiples montajes simultáneos
    Permite montar varios buckets en diferentes letras de unidad
    """
    
    def __init__(self, rclone_manager):
        self.rclone_manager = rclone_manager
        self.mounted_drives: Dict[str, MountInfo] = {}
        self._load_saved_mounts()
        
    def _load_saved_mounts(self):
        """Cargar montajes guardados de la sesión anterior"""
        try:
            saved_mounts = self.rclone_manager.config_manager.get_saved_mounts()
            if saved_mounts:
                for mount_data in saved_mounts:
                    mount_info = MountInfo.from_dict(mount_data)
                    # No auto-montar, solo cargar la info
                    mount_info.status = 'disconnected'
                    mount_info.process = None
                    self.mounted_drives[mount_info.letter] = mount_info
        except Exception as e:
            print(f"[MultipleMountManager] Error loading saved mounts: {e}")
    
    def _save_mounts(self):
        """Guardar montajes actuales"""
        try:
            mounts_data = [info.to_dict() for info in self.mounted_drives.values()]
            self.rclone_manager.config_manager.save_mounts(mounts_data)
        except Exception as e:
            print(f"[MultipleMountManager] Error saving mounts: {e}")
    
    def get_available_letters(self) -> List[str]:
        """Obtener letras de unidad disponibles"""
        import os
        used_letters = set()
        
        # Letras ya montadas por este manager
        used_letters.update(
            letter for letter, info in self.mounted_drives.items()
            if info.status == 'connected'
        )
        
        # Letras de unidades existentes en el sistema
        for letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
            if os.path.exists(f'{letter}:\\'):
                used_letters.add(letter)
        
        # Letras disponibles (priorizamos V-Z para montajes)
        preferred_letters = list('VWXYZ')
        available = [l for l in preferred_letters if l not in used_letters]
        
        # Si se acabaron las preferidas, usar otras
        if not available:
            available = [l for l in 'EFGHIJKLMNOPQRSTU' if l not in used_letters]
        
        return available
    
    def mount_drive(self, letter: str, profile: str, bucket: str) -> Tuple[bool, str]:
        """
        Montar un nuevo bucket
        
        Args:
            letter: Letra de unidad (V, W, X, etc.)
            profile: Nombre del perfil de configuración
            bucket: Nombre del bucket a montar
            
        Returns:
            (success, message)
        """
        # Validar que la letra esté disponible
        if letter in self.mounted_drives and self.mounted_drives[letter].status == 'connected':
            return False, f"La unidad {letter}: ya está en uso"
        
        if letter not in self.get_available_letters():
            return False, f"La letra {letter}: no está disponible"
        
        # Crear info del montaje
        mount_info = MountInfo(letter, profile, bucket)
        mount_info.status = 'mounting'
        self.mounted_drives[letter] = mount_info
        
        try:
            # Usar el rclone_manager existente para montar
            success, message, process = self.rclone_manager.mount_drive(
                profile,
                letter,
                bucket
            )
            
            if success:
                self.record_mount_success(letter, profile, bucket, process)
                return True, message or f"Bucket montado exitosamente en {letter}:"
            else:
                mount_info.status = 'error'
                mount_info.error_message = message
                self._save_mounts()
                return False, message
                
        except Exception as e:
            mount_info.status = 'error'
            mount_info.error_message = str(e)
            return False, f"Error al montar: {str(e)}"
    
    def unmount_drive(self, letter: str) -> Tuple[bool, str]:
        """
        Desmontar una unidad específica
        
        Args:
            letter: Letra de la unidad a desmontar
            
        Returns:
            (success, message)
        """
        if letter not in self.mounted_drives:
            return False, f"La unidad {letter}: no está montada"
        
        mount_info = self.mounted_drives[letter]
        
        try:
            # Desmontar usando el proceso guardado
            if mount_info.process:
                success, message = self.rclone_manager.unmount_drive_by_process(
                    mount_info.process
                )
            else:
                # Si no hay proceso, intentar matar por letra
                success, message = self.rclone_manager.unmount_drive_by_letter(letter)
            
            if success:
                self.record_unmount(letter)
                return True, f"Unidad {letter}: desmontada correctamente"
            else:
                return False, message
                
        except Exception as e:
            return False, f"Error al desmontar: {str(e)}"
    
    def remove_drive(self, letter: str) -> Tuple[bool, str]:
        """
        Remover completamente una unidad de la lista (desmontar si está montada)
        
        Args:
            letter: Letra de la unidad a remover
            
        Returns:
            (success, message)
        """
        if letter not in self.mounted_drives:
            return False, f"La unidad {letter}: no existe en la lista"
        
        mount_info = self.mounted_drives[letter]
        
        # Si está conectada, desmontar primero
        if mount_info.status == 'connected':
            success, message = self.unmount_drive(letter)
            if not success:
                return False, f"No se pudo desmontar: {message}"
        
        # Remover de la lista
        del self.mounted_drives[letter]
        self._save_mounts()
        
        return True, f"Unidad {letter}: removida de la lista"
    
    def unmount_all(self) -> Tuple[bool, str]:
        """Desmontar todas las unidades"""
        errors = []
        success_count = 0
        
        for letter in list(self.mounted_drives.keys()):
            mount_info = self.mounted_drives[letter]
            if mount_info.status == 'connected':
                success, message = self.unmount_drive(letter)
                if success:
                    success_count += 1
                else:
                    errors.append(f"{letter}: {message}")
        
        if errors:
            return False, f"Desmontadas {success_count}, errores: {', '.join(errors)}"
        else:
            return True, f"Todas las unidades desmontadas ({success_count})"
    
    def get_all_mounted(self) -> Dict[str, MountInfo]:
        """Obtener diccionario de todas las unidades (montadas y no montadas)"""
        return self.mounted_drives.copy()
    
    def get_mounted_count(self) -> int:
        """Obtener cantidad de unidades conectadas"""
        return sum(1 for info in self.mounted_drives.values() 
                  if info.status == 'connected')
    
    def get_status(self, letter: str) -> Optional[MountInfo]:
        """Obtener información de una unidad específica"""
        return self.mounted_drives.get(letter)
    
    def refresh_status(self, letter: str) -> bool:
        """
        Actualizar estado de una unidad verificando si realmente está montada
        
        Args:
            letter: Letra de la unidad
            
        Returns:
            True si está conectada, False si no
        """
        import os
        
        if letter not in self.mounted_drives:
            return False
        
        mount_info = self.mounted_drives[letter]
        
        # Verificar si la unidad existe en el sistema
        drive_path = f'{letter}:\\'
        is_mounted = os.path.exists(drive_path)
        
        # Verificar si el proceso sigue vivo
        process_alive = False
        if mount_info.process:
            try:
                process_alive = mount_info.process.poll() is None
            except:
                pass
        
        # Actualizar estado
        if is_mounted and process_alive:
            mount_info.status = 'connected'
        elif is_mounted and not process_alive:
            mount_info.status = 'connected'  # Montado por otro proceso
        else:
            mount_info.status = 'disconnected'
            mount_info.process = None
        
        return mount_info.status == 'connected'
    
    def refresh_all_status(self):
        """Actualizar estado de todas las unidades"""
        for letter in self.mounted_drives.keys():
            self.refresh_status(letter)

    def record_mount_success(self, letter: str, profile: str, bucket: str, process=None):
        mount_info = self.mounted_drives.get(letter)
        if mount_info is None:
            mount_info = MountInfo(letter, profile, bucket, process)
        else:
            mount_info.profile = profile
            mount_info.bucket = bucket
            mount_info.process = process
        mount_info.status = 'connected'
        mount_info.mounted_at = datetime.now()
        mount_info.error_message = None
        self.mounted_drives[letter] = mount_info
        self._save_mounts()

    def record_unmount(self, letter: str):
        mount_info = self.mounted_drives.get(letter)
        if mount_info:
            mount_info.status = 'disconnected'
            mount_info.process = None
            mount_info.error_message = None
            self._save_mounts()

    def get_mounts_list(self) -> List[MountInfo]:
        return [self.mounted_drives[letter] for letter in sorted(self.mounted_drives.keys())]

    def get_mounts_as_rows(self):
        """Obtener lista de montajes ordenados para UI"""
        result = []
        for letter in sorted(self.mounted_drives.keys()):
            info = self.mounted_drives[letter]
            result.append(info)
        return result
    
    def open_drive_in_explorer(self, letter: str) -> Tuple[bool, str]:
        """
        Abrir una unidad en el Explorador de Windows
        
        Args:
            letter: Letra de la unidad
            
        Returns:
            (success, message)
        """
        if letter not in self.mounted_drives:
            return False, f"La unidad {letter}: no existe"
        
        mount_info = self.mounted_drives[letter]
        
        if mount_info.status != 'connected':
            return False, f"La unidad {letter}: no está conectada"
        
        try:
            import subprocess
            subprocess.Popen(f'explorer {letter}:\\')
            return True, f"Explorador abierto en {letter}:"
        except Exception as e:
            return False, f"Error al abrir explorador: {str(e)}"

