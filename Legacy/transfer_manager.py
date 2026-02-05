"""
Transfer Manager - Gestor central de transferencias con persistencia y resume
"""
import json
import os
import uuid
from datetime import datetime
from typing import Dict, List, Optional
from PyQt6.QtCore import QObject, pyqtSignal, QThread
from dataclasses import dataclass, asdict
from enum import Enum


class TransferStatus(Enum):
    QUEUED = "queued"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    ERROR = "error"
    CANCELLED = "cancelled"


class TransferType(Enum):
    AZURE_TO_LOCAL = "azure_to_local"
    AZURE_TO_GCP = "azure_to_gcp"
    AZURE_TO_AZURE = "azure_to_azure"
    GCP_DOWNLOAD = "gcp_download"


@dataclass
class TransferInfo:
    """Información de una transferencia"""
    id: str
    transfer_type: str
    name: str
    source: str
    destination: str
    total_bytes: int
    bytes_transferred: int
    status: str
    created_at: str
    updated_at: str
    # Azure specific
    sas_url: Optional[str] = None
    sas_expiry: Optional[str] = None
    subscription_id: Optional[str] = None
    resource_group: Optional[str] = None
    disk_name: Optional[str] = None
    # GCP specific
    bucket_name: Optional[str] = None
    blob_name: Optional[str] = None
    # Error info
    error_message: Optional[str] = None
    
    def to_dict(self):
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)
    
    @property
    def progress_percent(self) -> int:
        if self.total_bytes <= 0:
            return 0
        return int((self.bytes_transferred / self.total_bytes) * 100)


class TransferManager(QObject):
    """Gestor central de todas las transferencias"""
    
    # Señales para UI
    transfer_added = pyqtSignal(str)  # transfer_id
    transfer_updated = pyqtSignal(str, int, str)  # transfer_id, progress%, status_text
    transfer_finished = pyqtSignal(str, bool, str)  # transfer_id, success, message
    transfer_removed = pyqtSignal(str)  # transfer_id
    
    def __init__(self, persist_path: str = None):
        super().__init__()
        self.persist_path = persist_path or os.path.join(os.getcwd(), "active_transfers.json")
        self.transfers: Dict[str, TransferInfo] = {}
        self.workers: Dict[str, QThread] = {}
        self._load_state()
    
    def _load_state(self):
        """Cargar estado de transferencias desde JSON"""
        if os.path.exists(self.persist_path):
            try:
                with open(self.persist_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for t_data in data.get("transfers", []):
                        t = TransferInfo.from_dict(t_data)
                        # Mark running transfers as paused (they were interrupted)
                        if t.status == TransferStatus.RUNNING.value:
                            t.status = TransferStatus.PAUSED.value
                        self.transfers[t.id] = t
            except Exception as e:
                print(f"Error loading transfer state: {e}")
    
    def _save_state(self):
        """Guardar estado de transferencias a JSON"""
        try:
            data = {
                "transfers": [t.to_dict() for t in self.transfers.values() 
                              if t.status not in [TransferStatus.COMPLETED.value, TransferStatus.CANCELLED.value]]
            }
            with open(self.persist_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving transfer state: {e}")
    
    def create_transfer(self, transfer_type: TransferType, name: str, source: str, 
                         destination: str, total_bytes: int = 0, **kwargs) -> str:
        """Crear una nueva transferencia y retornar su ID"""
        transfer_id = str(uuid.uuid4())[:8]
        now = datetime.now().isoformat()
        
        transfer = TransferInfo(
            id=transfer_id,
            transfer_type=transfer_type.value,
            name=name,
            source=source,
            destination=destination,
            total_bytes=total_bytes,
            bytes_transferred=0,
            status=TransferStatus.QUEUED.value,
            created_at=now,
            updated_at=now,
            **kwargs
        )
        
        self.transfers[transfer_id] = transfer
        self._save_state()
        self.transfer_added.emit(transfer_id)
        return transfer_id
    
    def update_progress(self, transfer_id: str, bytes_transferred: int, 
                        status_text: str = "", total_bytes: int = None):
        """Actualizar progreso de una transferencia"""
        if transfer_id not in self.transfers:
            return
        
        transfer = self.transfers[transfer_id]
        transfer.bytes_transferred = bytes_transferred
        if total_bytes:
            transfer.total_bytes = total_bytes
        transfer.updated_at = datetime.now().isoformat()
        transfer.status = TransferStatus.RUNNING.value
        
        self._save_state()
        self.transfer_updated.emit(transfer_id, transfer.progress_percent, status_text)
    
    def complete_transfer(self, transfer_id: str, success: bool, message: str = ""):
        """Marcar transferencia como completada"""
        if transfer_id not in self.transfers:
            return
        
        transfer = self.transfers[transfer_id]
        transfer.status = TransferStatus.COMPLETED.value if success else TransferStatus.ERROR.value
        transfer.updated_at = datetime.now().isoformat()
        if not success:
            transfer.error_message = message
        
        self._save_state()
        self.transfer_finished.emit(transfer_id, success, message)
        
        # Clean up worker reference
        if transfer_id in self.workers:
            del self.workers[transfer_id]
    
    def pause_transfer(self, transfer_id: str):
        """Pausar una transferencia"""
        if transfer_id not in self.transfers:
            return
        
        transfer = self.transfers[transfer_id]
        transfer.status = TransferStatus.PAUSED.value
        transfer.updated_at = datetime.now().isoformat()
        self._save_state()
        
        # Signal worker to stop (worker must check _should_stop flag)
        if transfer_id in self.workers:
            worker = self.workers[transfer_id]
            if hasattr(worker, 'stop'):
                worker.stop()
    
    def cancel_transfer(self, transfer_id: str):
        """Cancelar y eliminar una transferencia"""
        if transfer_id not in self.transfers:
            return
        
        # Stop worker first
        if transfer_id in self.workers:
            worker = self.workers[transfer_id]
            if hasattr(worker, 'stop'):
                worker.stop()
            del self.workers[transfer_id]
        
        transfer = self.transfers[transfer_id]
        transfer.status = TransferStatus.CANCELLED.value
        self._save_state()
        self.transfer_removed.emit(transfer_id)
    
    def get_transfer(self, transfer_id: str) -> Optional[TransferInfo]:
        return self.transfers.get(transfer_id)
    
    def get_all_transfers(self) -> List[TransferInfo]:
        return list(self.transfers.values())
    
    def get_resumable_transfers(self) -> List[TransferInfo]:
        """Obtener transferencias que pueden ser reanudadas"""
        return [t for t in self.transfers.values() 
                if t.status in [TransferStatus.PAUSED.value, TransferStatus.ERROR.value]
                and t.bytes_transferred > 0]
    
    def register_worker(self, transfer_id: str, worker: QThread):
        """Registrar un worker para una transferencia"""
        self.workers[transfer_id] = worker
    
    def cleanup_completed(self):
        """Limpiar transferencias completadas/canceladas"""
        to_remove = [tid for tid, t in self.transfers.items() 
                     if t.status in [TransferStatus.COMPLETED.value, TransferStatus.CANCELLED.value]]
        for tid in to_remove:
            del self.transfers[tid]
        self._save_state()


# Singleton global
_manager_instance: Optional[TransferManager] = None

def get_transfer_manager() -> TransferManager:
    """Obtener instancia singleton del TransferManager"""
    global _manager_instance
    if _manager_instance is None:
        _manager_instance = TransferManager()
    return _manager_instance
