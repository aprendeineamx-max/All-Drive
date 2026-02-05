"""
Audit Logger - Sistema de auditoría para operaciones importantes
Registra todas las operaciones críticas para trazabilidad y seguridad
"""

import json
import os
from datetime import datetime
from typing import Dict, Optional, List
from enum import Enum


class AuditEventType(Enum):
    """Tipos de eventos auditables"""
    PROFILE_CREATED = "profile_created"
    PROFILE_UPDATED = "profile_updated"
    PROFILE_DELETED = "profile_deleted"
    DRIVE_MOUNTED = "drive_mounted"
    DRIVE_UNMOUNTED = "drive_unmounted"
    FILE_UPLOADED = "file_uploaded"
    FILE_DELETED = "file_deleted"
    BUCKET_FORMATTED = "bucket_formatted"
    SYNC_STARTED = "sync_started"
    SYNC_STOPPED = "sync_stopped"
    BACKUP_STARTED = "backup_started"
    BACKUP_COMPLETED = "backup_completed"
    CONFIGURATION_CHANGED = "configuration_changed"
    ERROR_OCCURRED = "error_occurred"


class AuditLogger:
    """Logger de auditoría con persistencia en archivo"""
    
    def __init__(self, audit_file: Optional[str] = None, max_entries: int = 10000):
        """
        Inicializar el logger de auditoría
        
        Args:
            audit_file: Ruta al archivo de auditoría (None = auto)
            max_entries: Número máximo de entradas antes de rotar
        """
        if audit_file is None:
            import sys
            if getattr(sys, 'frozen', False):
                base_path = os.path.dirname(sys.executable)
            else:
                base_path = os.path.dirname(os.path.abspath(__file__))
            audit_dir = os.path.join(base_path, "logs")
            os.makedirs(audit_dir, exist_ok=True)
            audit_file = os.path.join(audit_dir, "audit.log")
        
        self.audit_file = audit_file
        self.max_entries = max_entries
        self._entries: List[Dict] = []
        self._load_entries()
    
    def _load_entries(self):
        """Cargar entradas existentes del archivo"""
        if os.path.exists(self.audit_file):
            try:
                with open(self.audit_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            try:
                                entry = json.loads(line)
                                self._entries.append(entry)
                            except json.JSONDecodeError:
                                continue
            except Exception:
                pass
    
    def _save_entry(self, entry: Dict):
        """Guardar una entrada en el archivo"""
        try:
            with open(self.audit_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(entry, ensure_ascii=False) + '\n')
        except Exception:
            pass  # Si falla, no bloquear la operación principal
    
    def _rotate_if_needed(self):
        """Rotar el archivo si tiene demasiadas entradas"""
        if len(self._entries) > self.max_entries:
            # Mantener solo las últimas max_entries
            self._entries = self._entries[-self.max_entries:]
            # Reescribir el archivo
            try:
                with open(self.audit_file, 'w', encoding='utf-8') as f:
                    for entry in self._entries:
                        f.write(json.dumps(entry, ensure_ascii=False) + '\n')
            except Exception:
                pass
    
    def log(self, event_type: AuditEventType, details: Dict, user: Optional[str] = None, 
            success: bool = True, error_message: Optional[str] = None):
        """
        Registrar un evento de auditoría
        
        Args:
            event_type: Tipo de evento
            details: Detalles del evento
            user: Usuario que realizó la acción (opcional)
            success: Si la operación fue exitosa
            error_message: Mensaje de error si hubo fallo
        """
        entry = {
            'timestamp': datetime.now().isoformat(),
            'event_type': event_type.value,
            'user': user or os.getenv('USERNAME', 'unknown'),
            'success': success,
            'details': details,
            'error_message': error_message
        }
        
        self._entries.append(entry)
        self._save_entry(entry)
        self._rotate_if_needed()
    
    def get_entries(self, event_type: Optional[AuditEventType] = None, 
                   limit: Optional[int] = None, 
                   since: Optional[datetime] = None) -> List[Dict]:
        """
        Obtener entradas de auditoría
        
        Args:
            event_type: Filtrar por tipo de evento
            limit: Límite de resultados
            since: Solo entradas desde esta fecha
        
        Returns:
            Lista de entradas de auditoría
        """
        entries = self._entries.copy()
        
        # Filtrar por tipo
        if event_type:
            entries = [e for e in entries if e.get('event_type') == event_type.value]
        
        # Filtrar por fecha
        if since:
            entries = [e for e in entries if datetime.fromisoformat(e['timestamp']) >= since]
        
        # Ordenar por timestamp (más recientes primero)
        entries.sort(key=lambda x: x['timestamp'], reverse=True)
        
        # Aplicar límite
        if limit:
            entries = entries[:limit]
        
        return entries
    
    def get_statistics(self) -> Dict:
        """Obtener estadísticas de auditoría"""
        total = len(self._entries)
        by_type = {}
        by_success = {'success': 0, 'failed': 0}
        
        for entry in self._entries:
            event_type = entry.get('event_type', 'unknown')
            by_type[event_type] = by_type.get(event_type, 0) + 1
            
            if entry.get('success', True):
                by_success['success'] += 1
            else:
                by_success['failed'] += 1
        
        return {
            'total_events': total,
            'by_type': by_type,
            'by_success': by_success,
            'oldest_entry': self._entries[0]['timestamp'] if self._entries else None,
            'newest_entry': self._entries[-1]['timestamp'] if self._entries else None
        }


# Instancia global del logger de auditoría
_audit_logger_instance: Optional[AuditLogger] = None


def get_audit_logger() -> AuditLogger:
    """Obtener la instancia global del logger de auditoría"""
    global _audit_logger_instance
    if _audit_logger_instance is None:
        _audit_logger_instance = AuditLogger()
    return _audit_logger_instance

