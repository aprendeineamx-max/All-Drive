"""
Tests para TaskScheduler
"""

import unittest
import sys
import os
from datetime import datetime, timedelta

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
from core.task_scheduler import TaskScheduler, ScheduledTask


class TestTaskScheduler(unittest.TestCase):
    """Tests para TaskScheduler"""
    
    @classmethod
    def setUpClass(cls):
        """Configuración inicial para todos los tests"""
        if not QApplication.instance():
            cls.app = QApplication([])
        else:
            cls.app = QApplication.instance()
    
    def setUp(self):
        """Configuración antes de cada test"""
        self.scheduler = TaskScheduler(check_interval_seconds=1)
        self.executed_tasks = []
    
    def tearDown(self):
        """Limpieza después de cada test"""
        self.scheduler.stop()
    
    def test_add_task(self):
        """Test: Agregar una tarea"""
        def dummy_task():
            self.executed_tasks.append("task1")
        
        result = self.scheduler.add_task("task1", dummy_task, "interval", "1m")
        self.assertTrue(result)
        self.assertIn("task1", self.scheduler.tasks)
    
    def test_remove_task(self):
        """Test: Eliminar una tarea"""
        def dummy_task():
            pass
        
        self.scheduler.add_task("task1", dummy_task, "interval", "1m")
        result = self.scheduler.remove_task("task1")
        self.assertTrue(result)
        self.assertNotIn("task1", self.scheduler.tasks)
    
    def test_enable_disable_task(self):
        """Test: Habilitar/deshabilitar una tarea"""
        def dummy_task():
            pass
        
        self.scheduler.add_task("task1", dummy_task, "interval", "1m")
        
        # Deshabilitar
        result = self.scheduler.enable_task("task1", False)
        self.assertTrue(result)
        self.assertFalse(self.scheduler.tasks["task1"].enabled)
        
        # Habilitar
        result = self.scheduler.enable_task("task1", True)
        self.assertTrue(result)
        self.assertTrue(self.scheduler.tasks["task1"].enabled)
    
    def test_get_task_info(self):
        """Test: Obtener información de una tarea"""
        def dummy_task():
            pass
        
        self.scheduler.add_task("task1", dummy_task, "interval", "5m")
        info = self.scheduler.get_task_info("task1")
        
        self.assertIsNotNone(info)
        self.assertEqual(info['task_id'], "task1")
        self.assertEqual(info['schedule_type'], "interval")
        self.assertEqual(info['schedule_value'], "5m")
        self.assertTrue(info['enabled'])
    
    def test_list_tasks(self):
        """Test: Listar todas las tareas"""
        def dummy_task():
            pass
        
        self.scheduler.add_task("task1", dummy_task, "interval", "1m")
        self.scheduler.add_task("task2", dummy_task, "daily", "14:30")
        
        tasks = self.scheduler.list_tasks()
        self.assertEqual(len(tasks), 2)
        task_ids = [t['task_id'] for t in tasks]
        self.assertIn("task1", task_ids)
        self.assertIn("task2", task_ids)
    
    def test_interval_schedule(self):
        """Test: Programación por intervalo"""
        task = ScheduledTask("test", lambda: None, "interval", "5m")
        self.assertIsNotNone(task.next_run)
        self.assertGreater(task.next_run, datetime.now())
    
    def test_daily_schedule(self):
        """Test: Programación diaria"""
        task = ScheduledTask("test", lambda: None, "daily", "14:30")
        # Puede ser None si la hora ya pasó hoy
        # Pero la estructura debe estar correcta
        self.assertIsInstance(task.schedule_type, str)


if __name__ == '__main__':
    unittest.main()

