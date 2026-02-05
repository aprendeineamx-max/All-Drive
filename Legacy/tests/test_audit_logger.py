"""
Tests para AuditLogger
"""

import unittest
import sys
import os
import tempfile
import json
from datetime import datetime

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.audit_logger import AuditLogger, AuditEventType, get_audit_logger


class TestAuditLogger(unittest.TestCase):
    """Tests para AuditLogger"""
    
    def setUp(self):
        """Configuración antes de cada test"""
        # Usar un archivo temporal para cada test
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.log')
        self.temp_file.close()
        self.audit_logger = AuditLogger(audit_file=self.temp_file.name)
    
    def tearDown(self):
        """Limpieza después de cada test"""
        # Eliminar el archivo temporal
        try:
            os.unlink(self.temp_file.name)
        except:
            pass
    
    def test_log_event(self):
        """Test: Registrar un evento"""
        self.audit_logger.log(
            AuditEventType.PROFILE_CREATED,
            {'profile_name': 'test_profile'},
            user='test_user',
            success=True
        )
        
        entries = self.audit_logger.get_entries()
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]['event_type'], 'profile_created')
        self.assertEqual(entries[0]['user'], 'test_user')
        self.assertTrue(entries[0]['success'])
    
    def test_log_error_event(self):
        """Test: Registrar un evento con error"""
        self.audit_logger.log(
            AuditEventType.ERROR_OCCURRED,
            {'operation': 'mount', 'drive_letter': 'V'},
            success=False,
            error_message='Connection failed'
        )
        
        entries = self.audit_logger.get_entries()
        self.assertEqual(len(entries), 1)
        self.assertFalse(entries[0]['success'])
        self.assertEqual(entries[0]['error_message'], 'Connection failed')
    
    def test_get_entries_by_type(self):
        """Test: Filtrar entradas por tipo"""
        self.audit_logger.log(AuditEventType.PROFILE_CREATED, {'name': 'p1'})
        self.audit_logger.log(AuditEventType.DRIVE_MOUNTED, {'drive': 'V'})
        self.audit_logger.log(AuditEventType.PROFILE_CREATED, {'name': 'p2'})
        
        entries = self.audit_logger.get_entries(event_type=AuditEventType.PROFILE_CREATED)
        self.assertEqual(len(entries), 2)
        for entry in entries:
            self.assertEqual(entry['event_type'], 'profile_created')
    
    def test_get_entries_with_limit(self):
        """Test: Limitar número de entradas"""
        for i in range(10):
            self.audit_logger.log(AuditEventType.FILE_UPLOADED, {'file': f'file{i}.txt'})
        
        entries = self.audit_logger.get_entries(limit=5)
        self.assertEqual(len(entries), 5)
    
    def test_get_statistics(self):
        """Test: Obtener estadísticas"""
        self.audit_logger.log(AuditEventType.PROFILE_CREATED, {'name': 'p1'}, success=True)
        self.audit_logger.log(AuditEventType.DRIVE_MOUNTED, {'drive': 'V'}, success=True)
        self.audit_logger.log(AuditEventType.ERROR_OCCURRED, {'op': 'test'}, success=False)
        
        stats = self.audit_logger.get_statistics()
        self.assertEqual(stats['total_events'], 3)
        self.assertEqual(stats['by_success']['success'], 2)
        self.assertEqual(stats['by_success']['failed'], 1)
        self.assertIn('profile_created', stats['by_type'])
        self.assertIn('drive_mounted', stats['by_type'])
    
    def test_get_audit_logger_singleton(self):
        """Test: Verificar que get_audit_logger retorna singleton"""
        logger1 = get_audit_logger()
        logger2 = get_audit_logger()
        self.assertIs(logger1, logger2)


if __name__ == '__main__':
    unittest.main()

