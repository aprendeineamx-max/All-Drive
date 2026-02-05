"""
Tests para StateMonitor
"""

import unittest
import sys
import os
from datetime import datetime

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtWidgets import QApplication
from core.state_monitor import StateMonitor, ComponentStatus, get_state_monitor


class TestStateMonitor(unittest.TestCase):
    """Tests para StateMonitor"""
    
    @classmethod
    def setUpClass(cls):
        """Configuración inicial para todos los tests"""
        if not QApplication.instance():
            cls.app = QApplication([])
        else:
            cls.app = QApplication.instance()
    
    def setUp(self):
        """Configuración antes de cada test"""
        self.monitor = StateMonitor()
    
    def test_register_component(self):
        """Test: Registrar un componente"""
        self.monitor.register_component("test_component", ComponentStatus.READY)
        
        status = self.monitor.get_component_status("test_component")
        self.assertIsNotNone(status)
        self.assertEqual(status['status'], 'ready')
    
    def test_update_component_status(self):
        """Test: Actualizar estado de componente"""
        self.monitor.register_component("test_component", ComponentStatus.INITIALIZING)
        self.monitor.update_component_status("test_component", ComponentStatus.READY)
        
        status = self.monitor.get_component_status("test_component")
        self.assertEqual(status['status'], 'ready')
    
    def test_get_all_statuses(self):
        """Test: Obtener todos los estados"""
        self.monitor.register_component("comp1", ComponentStatus.READY)
        self.monitor.register_component("comp2", ComponentStatus.RUNNING)
        
        all_statuses = self.monitor.get_all_statuses()
        self.assertEqual(len(all_statuses), 2)
        self.assertIn("comp1", all_statuses)
        self.assertIn("comp2", all_statuses)
    
    def test_set_get_metric(self):
        """Test: Establecer y obtener métricas"""
        self.monitor.set_metric("cpu_usage", 45.5)
        self.monitor.set_metric("memory_mb", 1024)
        
        cpu = self.monitor.get_metric("cpu_usage")
        memory = self.monitor.get_metric("memory_mb")
        
        self.assertEqual(cpu, 45.5)
        self.assertEqual(memory, 1024)
    
    def test_get_all_metrics(self):
        """Test: Obtener todas las métricas"""
        self.monitor.set_metric("metric1", 10)
        self.monitor.set_metric("metric2", 20)
        
        all_metrics = self.monitor.get_all_metrics()
        self.assertEqual(len(all_metrics), 2)
        self.assertEqual(all_metrics['metric1'], 10)
        self.assertEqual(all_metrics['metric2'], 20)
    
    def test_get_health_summary(self):
        """Test: Obtener resumen de salud"""
        self.monitor.register_component("comp1", ComponentStatus.READY, {'critical': True})
        self.monitor.register_component("comp2", ComponentStatus.RUNNING)
        
        summary = self.monitor.get_health_summary()
        self.assertIn('is_healthy', summary)
        self.assertIn('total_components', summary)
        self.assertIn('by_status', summary)
        self.assertEqual(summary['total_components'], 2)
    
    def test_get_state_monitor_singleton(self):
        """Test: Verificar que get_state_monitor retorna singleton"""
        monitor1 = get_state_monitor()
        monitor2 = get_state_monitor()
        self.assertIs(monitor1, monitor2)


if __name__ == '__main__':
    unittest.main()

