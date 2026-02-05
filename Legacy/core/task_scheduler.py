"""
Task Scheduler - Sistema de programación de tareas
Permite programar operaciones como sincronizaciones, backups, etc.
"""

from PyQt6.QtCore import QObject, QTimer, pyqtSignal
from datetime import datetime, time as dt_time
from typing import Callable, Optional, Dict, List
import threading


class ScheduledTask:
    """Representa una tarea programada"""
    
    def __init__(self, task_id: str, callback: Callable, schedule_type: str, 
                 schedule_value: str, enabled: bool = True, last_run: Optional[datetime] = None):
        self.task_id = task_id
        self.callback = callback
        self.schedule_type = schedule_type  # 'interval', 'daily', 'weekly', 'once'
        self.schedule_value = schedule_value  # '5m', '14:30', 'monday 09:00', '2024-12-25 10:00'
        self.enabled = enabled
        self.last_run = last_run
        self.next_run: Optional[datetime] = None
        self.run_count = 0
        self.error_count = 0
        self._calculate_next_run()
    
    def _calculate_next_run(self):
        """Calcular cuándo debe ejecutarse la próxima vez"""
        now = datetime.now()
        
        if self.schedule_type == 'interval':
            # schedule_value es como "5m", "1h", "30s"
            import re
            match = re.match(r'(\d+)([smhd])', self.schedule_value.lower())
            if match:
                value, unit = int(match.group(1)), match.group(2)
                from datetime import timedelta
                if unit == 's':
                    delta = timedelta(seconds=value)
                elif unit == 'm':
                    delta = timedelta(minutes=value)
                elif unit == 'h':
                    delta = timedelta(hours=value)
                elif unit == 'd':
                    delta = timedelta(days=value)
                else:
                    delta = timedelta(minutes=5)  # Default
                self.next_run = now + delta
        
        elif self.schedule_type == 'daily':
            # schedule_value es como "14:30"
            try:
                hour, minute = map(int, self.schedule_value.split(':'))
                next_time = dt_time(hour, minute)
                today = datetime.combine(now.date(), next_time)
                if today <= now:
                    from datetime import timedelta
                    today += timedelta(days=1)
                self.next_run = today
            except:
                self.next_run = None
        
        elif self.schedule_type == 'weekly':
            # schedule_value es como "monday 09:00"
            # Implementación simplificada - solo para hoy si es el día correcto
            self.next_run = None  # TODO: Implementar lógica completa
        
        elif self.schedule_type == 'once':
            # schedule_value es como "2024-12-25 10:00"
            try:
                self.next_run = datetime.strptime(self.schedule_value, "%Y-%m-%d %H:%M")
                if self.next_run <= now:
                    self.next_run = None  # Ya pasó
            except:
                self.next_run = None
    
    def should_run(self) -> bool:
        """Verificar si la tarea debe ejecutarse ahora"""
        if not self.enabled or not self.next_run:
            return False
        return datetime.now() >= self.next_run
    
    def execute(self):
        """Ejecutar la tarea"""
        try:
            self.callback()
            self.last_run = datetime.now()
            self.run_count += 1
            self._calculate_next_run()
            return True
        except Exception as e:
            self.error_count += 1
            raise e


class TaskScheduler(QObject):
    """Scheduler de tareas con soporte para múltiples tipos de programación"""
    
    task_executed = pyqtSignal(str, bool, str)  # task_id, success, message
    task_error = pyqtSignal(str, str)  # task_id, error_message
    
    def __init__(self, check_interval_seconds: int = 60):
        super().__init__()
        self.tasks: Dict[str, ScheduledTask] = {}
        self.check_interval = check_interval_seconds * 1000  # Convertir a ms
        self.timer = QTimer()
        self.timer.timeout.connect(self._check_and_execute)
        self.running = False
    
    def start(self):
        """Iniciar el scheduler"""
        if not self.running:
            self.running = True
            self.timer.start(self.check_interval)
    
    def stop(self):
        """Detener el scheduler"""
        if self.running:
            self.running = False
            self.timer.stop()
    
    def add_task(self, task_id: str, callback: Callable, schedule_type: str, 
                 schedule_value: str, enabled: bool = True) -> bool:
        """
        Agregar una tarea programada
        
        Args:
            task_id: Identificador único de la tarea
            callback: Función a ejecutar
            schedule_type: Tipo de programación ('interval', 'daily', 'weekly', 'once')
            schedule_value: Valor de la programación
            enabled: Si está habilitada
        
        Returns:
            True si se agregó correctamente
        """
        if task_id in self.tasks:
            return False
        
        task = ScheduledTask(task_id, callback, schedule_type, schedule_value, enabled)
        self.tasks[task_id] = task
        return True
    
    def remove_task(self, task_id: str) -> bool:
        """Eliminar una tarea"""
        if task_id in self.tasks:
            del self.tasks[task_id]
            return True
        return False
    
    def enable_task(self, task_id: str, enabled: bool = True) -> bool:
        """Habilitar o deshabilitar una tarea"""
        if task_id in self.tasks:
            self.tasks[task_id].enabled = enabled
            if enabled:
                self.tasks[task_id]._calculate_next_run()
            return True
        return False
    
    def get_task_info(self, task_id: str) -> Optional[Dict]:
        """Obtener información de una tarea"""
        if task_id not in self.tasks:
            return None
        
        task = self.tasks[task_id]
        return {
            'task_id': task.task_id,
            'schedule_type': task.schedule_type,
            'schedule_value': task.schedule_value,
            'enabled': task.enabled,
            'last_run': task.last_run.isoformat() if task.last_run else None,
            'next_run': task.next_run.isoformat() if task.next_run else None,
            'run_count': task.run_count,
            'error_count': task.error_count
        }
    
    def list_tasks(self) -> List[Dict]:
        """Listar todas las tareas"""
        return [self.get_task_info(task_id) for task_id in self.tasks.keys()]
    
    def _check_and_execute(self):
        """Verificar y ejecutar tareas pendientes"""
        now = datetime.now()
        for task_id, task in list(self.tasks.items()):
            if task.should_run():
                try:
                    success = task.execute()
                    self.task_executed.emit(task_id, success, "Tarea ejecutada correctamente")
                except Exception as e:
                    error_msg = str(e)
                    self.task_error.emit(task_id, error_msg)
                    # Recalcular próxima ejecución incluso si falló
                    task._calculate_next_run()

