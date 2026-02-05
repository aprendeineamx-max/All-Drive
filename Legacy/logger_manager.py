import logging
import logging.handlers
import sys
import os
from enum import IntEnum
from PyQt6.QtCore import QObject, pyqtSignal

class LogLevel(IntEnum):
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL

class QtLogHandler(logging.Handler, QObject):
    """Handler que emite señales Qt para la UI"""
    new_log = pyqtSignal(str, str, str)  # timestamp, level, message

    def __init__(self):
        logging.Handler.__init__(self)
        QObject.__init__(self)
        self.setFormatter(logging.Formatter('%(asctime)s | %(levelname)s | %(name)s | %(message)s', datefmt='%H:%M:%S'))

    def emit(self, record):
        msg = self.format(record)
        # Parsear para estructurar
        try:
            parts = msg.split('|', 3)
            if len(parts) >= 4:
                self.new_log.emit(parts[0].strip(), parts[1].strip(), parts[3].strip())
            else:
                self.new_log.emit("", record.levelname, record.getMessage())
        except:
             self.new_log.emit("", "ERROR", "Log parsing failed")

class LoggerManager(QObject): # Heredar de QObject para señales
    """
    Gestor centralizado de logging para VultrDrive Desktop
    ...
    """
    # Signal global por conveniencia
    log_received = pyqtSignal(str, str, str)

    def __init__(self, app_name="VultrDrive", log_dir=None, max_bytes=10*1024*1024, backup_count=5):
        QObject.__init__(self) # Initialize QObject
        
        self.app_name = app_name
        self.log_dir = log_dir or self._get_default_log_dir()
        self.max_bytes = max_bytes
        self.backup_count = backup_count
        
        os.makedirs(self.log_dir, exist_ok=True)
        
        self.logger = logging.getLogger(app_name)
        self.logger.setLevel(logging.DEBUG)
        
        # Evitar duplicación de handlers si se reinicia
        self.logger.handlers = [] 
        
        # Formatos
        self.file_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        self.console_formatter = logging.Formatter('%(levelname)-8s | %(message)s')
        
        self._setup_file_handler()
        self._setup_console_handler()
        self._setup_qt_handler() # Nuevo handler para UI

        self.logger.info(f"Logger inicializado. Logs en: {self.log_dir}")

    # ... _get_default_log_dir, _setup_file_handler, _setup_console_handler idénticos ...
    def _get_default_log_dir(self):
        if getattr(sys, 'frozen', False):
            base_path = os.path.dirname(sys.executable)
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(base_path, "logs")
    
    def _setup_file_handler(self):
        log_file = os.path.join(self.log_dir, f"{self.app_name}.log")
        file_handler = logging.handlers.RotatingFileHandler(
            log_file, maxBytes=self.max_bytes, backupCount=self.backup_count, encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(self.file_formatter)
        self.logger.addHandler(file_handler)
    
    def _setup_console_handler(self):
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(self.console_formatter)
        self.logger.addHandler(console_handler)

    def _setup_qt_handler(self):
        """Configurar handler para señales Qt"""
        self.qt_handler = QtLogHandler()
        self.qt_handler.setLevel(logging.DEBUG)
        # Conectar señal del handler a señal del manager
        self.qt_handler.new_log.connect(self.log_received.emit)
        self.logger.addHandler(self.qt_handler)

    def upload_logs_to_cloud(self, bucket_name="desktop-backups"):
        """Compone un ZIP con todos los logs y lo sube a la nube"""
        import zipfile
        import subprocess
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            zip_path = os.path.join(self.log_dir, f"logs_{timestamp}.zip")
            
            self.info("Empaquetando logs para subida...")
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(self.log_dir):
                    for file in files:
                        if file.endswith(".log") or file.endswith(".log.1"):
                            zipf.write(os.path.join(root, file), file)
            
            # Subir con Rclone
            # Nota: Esto asume que rclone está en PATH o gestionado por rclone_manager.
            # Idealmente usaríamos RcloneManager, pero para evitar deps circulares usamos subprocess simple.
            remote_path = f"vultr:{bucket_name}/diagnostics/{os.environ.get('COMPUTERNAME')}_logs_{timestamp}.zip"
            self.info(f"Subiendo logs a {remote_path}...")
            
            # TODO: Localizar rclone mejor
            res = subprocess.run(["rclone", "copyto", zip_path, remote_path], capture_output=True, text=True)
            
            if res.returncode == 0:
                self.info("✅ Logs subidos correctamente.")
                return True, "Subida exitosa"
            else:
                self.error(f"❌ Error subiendo logs: {res.stderr}")
                return False, res.stderr
                
        except Exception as e:
            self.exception("Error critical en upload_logs_to_cloud")
            return False, str(e)

    # Resto de métodos proxy (debug, info, etc) se mantienen...
    def set_console_level(self, level: LogLevel):
        for h in self.logger.handlers:
            if isinstance(h, logging.StreamHandler) and not isinstance(h, logging.handlers.RotatingFileHandler):
                h.setLevel(level.value)
    
    def set_file_level(self, level: LogLevel):
        for h in self.logger.handlers:
            if isinstance(h, logging.handlers.RotatingFileHandler):
                h.setLevel(level.value)
    
    def get_logger(self, name=None):
        if name: return logging.getLogger(f"{self.app_name}.{name}")
        return self.logger
    
    def debug(self, msg, *args, **kwargs): self.logger.debug(msg, *args, **kwargs)
    def info(self, msg, *args, **kwargs): self.logger.info(msg, *args, **kwargs)
    def warning(self, msg, *args, **kwargs): self.logger.warning(msg, *args, **kwargs)
    def error(self, msg, *args, **kwargs): self.logger.error(msg, *args, **kwargs)
    def critical(self, msg, *args, **kwargs): self.logger.critical(msg, *args, **kwargs)
    def exception(self, msg, *args, **kwargs): self.logger.exception(msg, *args, **kwargs)
    
    def get_log_files(self):
        log_files = []
        base_log = os.path.join(self.log_dir, f"{self.app_name}.log")
        if os.path.exists(base_log): log_files.append(base_log)
        for i in range(1, self.backup_count + 1):
            f = f"{base_log}.{i}"
            if os.path.exists(f): log_files.append(f)
        return log_files

    def clear_old_logs(self, days=30):
        # Implementación idéntica a la original...
        from datetime import timedelta
        cutoff = datetime.now() - timedelta(days=days)
        deleted = 0
        for f in self.get_log_files():
            try:
                if datetime.fromtimestamp(os.path.getmtime(f)) < cutoff:
                    os.remove(f)
                    deleted += 1
            except: pass
        return deleted

# Singleton global (ajustado)
_logger_manager_instance = None

def get_logger_manager(app_name="VultrDrive", log_dir=None) -> LoggerManager:
    global _logger_manager_instance
    if _logger_manager_instance is None:
        _logger_manager_instance = LoggerManager(app_name, log_dir)
    return _logger_manager_instance

def get_logger(name=None):
    return get_logger_manager().get_logger(name)

