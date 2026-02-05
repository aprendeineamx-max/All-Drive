"""
State Monitor - Monitor global del estado de la aplicación
Rastrea el estado de componentes, conexiones, montajes, etc.
"""

from PyQt6.QtCore import QObject, pyqtSignal, QTimer
from datetime import datetime
from typing import Dict, Optional, List, Any
from enum import Enum


class ComponentStatus(Enum):
    """Estados posibles de un componente"""
    UNKNOWN = "unknown"
    INITIALIZING = "initializing"
    READY = "ready"
    RUNNING = "running"
    WARNING = "warning"
    ERROR = "error"
    STOPPED = "stopped"


class StateMonitor(QObject):
    """Monitor global del estado de la aplicación"""
    
    status_changed = pyqtSignal(str, str, str)  # component, old_status, new_status
    health_changed = pyqtSignal(bool)  # is_healthy
    
    def __init__(self):
        super().__init__()
        self.components: Dict[str, Dict[str, Any]] = {}
        self.metrics: Dict[str, Any] = {}
        self.last_update = datetime.now()
        self._update_timer = QTimer()
        self._update_timer.timeout.connect(self._periodic_update)
        self._update_timer.start(5000)  # Actualizar cada 5 segundos
    
    def register_component(self, component_id: str, initial_status: ComponentStatus = ComponentStatus.UNKNOWN,
                          metadata: Optional[Dict] = None):
        """
        Registrar un componente para monitoreo
        
        Args:
            component_id: Identificador único del componente
            initial_status: Estado inicial
            metadata: Metadatos adicionales del componente
        """
        self.components[component_id] = {
            'status': initial_status.value,
            'status_enum': initial_status,
            'metadata': metadata or {},
            'last_update': datetime.now().isoformat(),
            'status_history': []
        }
        self._add_status_history(component_id, initial_status.value)
    
    def update_component_status(self, component_id: str, status: ComponentStatus, 
                               metadata: Optional[Dict] = None):
        """
        Actualizar el estado de un componente
        
        Args:
            component_id: Identificador del componente
            status: Nuevo estado
            metadata: Metadatos adicionales a actualizar
        """
        if component_id not in self.components:
            self.register_component(component_id, status, metadata)
            return
        
        old_status = self.components[component_id]['status']
        new_status = status.value
        
        if old_status != new_status:
            self.components[component_id]['status'] = new_status
            self.components[component_id]['status_enum'] = status
            self.components[component_id]['last_update'] = datetime.now().isoformat()
            self._add_status_history(component_id, new_status)
            
            if metadata:
                self.components[component_id]['metadata'].update(metadata)
            
            self.status_changed.emit(component_id, old_status, new_status)
            self._check_health()
    
    def _add_status_history(self, component_id: str, status: str):
        """Agregar entrada al historial de estados"""
        history = self.components[component_id]['status_history']
        history.append({
            'status': status,
            'timestamp': datetime.now().isoformat()
        })
        # Mantener solo las últimas 50 entradas
        if len(history) > 50:
            history.pop(0)
    
    def get_component_status(self, component_id: str) -> Optional[Dict]:
        """Obtener el estado de un componente"""
        return self.components.get(component_id)
    
    def get_all_statuses(self) -> Dict[str, Dict]:
        """Obtener el estado de todos los componentes"""
        return self.components.copy()
    
    def set_metric(self, metric_name: str, value: Any):
        """Establecer una métrica"""
        self.metrics[metric_name] = {
            'value': value,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_metric(self, metric_name: str) -> Optional[Any]:
        """Obtener el valor de una métrica"""
        metric = self.metrics.get(metric_name)
        return metric['value'] if metric else None
    
    def get_all_metrics(self) -> Dict[str, Any]:
        """Obtener todas las métricas"""
        return {k: v['value'] for k, v in self.metrics.items()}
    
    def _check_health(self):
        """Verificar la salud general del sistema"""
        is_healthy = True
        
        # Verificar si hay componentes en error
        for component_id, component_data in self.components.items():
            status = component_data['status']
            if status in [ComponentStatus.ERROR.value, ComponentStatus.STOPPED.value]:
                # Algunos componentes pueden estar detenidos sin ser un problema
                if component_id not in ['sync', 'backup']:  # Estos pueden estar detenidos normalmente
                    is_healthy = False
                    break
        
        self.health_changed.emit(is_healthy)
    
    def _periodic_update(self):
        """Actualización periódica del monitor"""
        self.last_update = datetime.now()
        
        # Verificar componentes que no se han actualizado en mucho tiempo
        now = datetime.now()
        for component_id, component_data in list(self.components.items()):
            last_update_str = component_data.get('last_update')
            if last_update_str:
                try:
                    last_update = datetime.fromisoformat(last_update_str)
                    delta = (now - last_update).total_seconds()
                    # Si no se actualiza en 5 minutos, marcar como warning
                    if delta > 300 and component_data['status'] not in [
                        ComponentStatus.STOPPED.value, 
                        ComponentStatus.ERROR.value
                    ]:
                        self.update_component_status(
                            component_id, 
                            ComponentStatus.WARNING,
                            {'reason': 'no_update_timeout'}
                        )
                except Exception:
                    pass
    
    def get_health_summary(self) -> Dict:
        """Obtener un resumen del estado de salud del sistema"""
        total = len(self.components)
        by_status = {}
        
        for component_data in self.components.values():
            status = component_data['status']
            by_status[status] = by_status.get(status, 0) + 1
        
        is_healthy = all(
            comp['status'] not in [ComponentStatus.ERROR.value] 
            for comp in self.components.values()
            if comp.get('metadata', {}).get('critical', False)
        )
        
        return {
            'is_healthy': is_healthy,
            'total_components': total,
            'by_status': by_status,
            'last_update': self.last_update.isoformat(),
            'metrics_count': len(self.metrics)
        }


# Instancia global del monitor
_state_monitor_instance: Optional[StateMonitor] = None


def get_state_monitor() -> StateMonitor:
    """Obtener la instancia global del monitor de estado"""
    global _state_monitor_instance
    if _state_monitor_instance is None:
        _state_monitor_instance = StateMonitor()
    return _state_monitor_instance

