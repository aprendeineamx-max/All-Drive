import sys
import json
import os

# ===== MEJORA #47: Sistema de Logging Robusto =====
try:
    from logger_manager import get_logger_manager
    logger_manager = get_logger_manager("VultrDrive")
    logger = logger_manager.get_logger()
    LOGGING_AVAILABLE = True
except ImportError:
    LOGGING_AVAILABLE = False
    logger = None
    print("[app] Advertencia: logger_manager no disponible. Usando print() para logging.")

try:
    import ctypes
except ImportError:  # pragma: no cover
    ctypes = None

def get_base_path():
    """Get the base path for the application (works with PyInstaller)"""
    if getattr(sys, 'frozen', False):
        # Ejecutando desde ejecutable empaquetado
        return os.path.dirname(sys.executable)
    else:
        # Ejecutando desde script Python
        return os.path.dirname(os.path.abspath(__file__))

def load_user_preferences():
    """Load user preferences for language and theme"""
    base_path = get_base_path()
    preferences_file = os.path.join(base_path, "user_preferences.json")
    default_preferences = {
        "language": "es",
        "theme": "dark"
    }
    
    try:
        if os.path.exists(preferences_file):
            with open(preferences_file, "r", encoding="utf-8") as f:
                return json.load(f)
        else:
            return default_preferences
    except:
        return default_preferences

def save_user_preferences(preferences):
    """Save user preferences for language and theme"""
    base_path = get_base_path()
    preferences_file = os.path.join(base_path, "user_preferences.json")
    try:
        with open(preferences_file, "w", encoding="utf-8") as f:
            json.dump(preferences, f, indent=2)
    except:
        pass

def check_winfsp():
    """
    Verifica si WinFsp está instalado (ultra-rápido: <1ms)
    Retorna: bool - True si está instalado, False si no
    """
    winfsp_paths = [
        r"C:\Program Files (x86)\WinFsp\bin\winfsp-x64.dll",
        r"C:\Program Files\WinFsp\bin\winfsp-x64.dll"
    ]
    
    for path in winfsp_paths:
        if os.path.exists(path):
            return True
    
    return False

def install_winfsp_silent():
    """Instala WinFsp de forma silenciosa con privilegios de administrador"""
    import subprocess
    import os
    import time

    def run_msiexec_admin(path):
        """Ejecuta el instalador MSI con privilegios de administrador"""
        try:
            # Comando PowerShell mejorado para instalación silenciosa
            ps_command = f"""
$process = Start-Process -FilePath 'msiexec.exe' -ArgumentList '/i', '"{path}"', '/quiet', '/norestart' -Verb RunAs -PassThru -Wait
exit $process.ExitCode
"""
            result = subprocess.run(
                ['powershell', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-Command', ps_command],
                check=False,
                timeout=300,  # 5 minutos de timeout
                capture_output=True,
                text=True
            )
            print(f"[WinFsp Installer] MSI Exit Code: {result.returncode}")
            if result.stdout:
                print(f"[WinFsp Installer] Output: {result.stdout}")
            if result.stderr:
                print(f"[WinFsp Installer] Errors: {result.stderr}")
            return result.returncode == 0
        except subprocess.TimeoutExpired:
            print("[WinFsp Installer] Timeout durante la instalación")
            return False
        except Exception as e:
            print(f"[WinFsp Installer] Error: {e}")
            return False

    try:
        base_path = get_base_path()
        
        # Buscar el instalador MSI en múltiples ubicaciones
        msi_files = []
        search_paths = [
            os.path.join(base_path, "dependencies"),
            os.path.join(base_path, "winfsp"),
            base_path
        ]
        
        print("[WinFsp Installer] Buscando instalador MSI...")
        for directory in search_paths:
            if os.path.isdir(directory):
                for file in os.listdir(directory):
                    if file.lower().startswith("winfsp") and file.lower().endswith(".msi"):
                        full_path = os.path.join(directory, file)
                        msi_files.append(full_path)
                        print(f"[WinFsp Installer] Encontrado: {full_path}")

        if not msi_files:
            print("[WinFsp Installer] No se encontró ningún instalador MSI")
            return False

        # Usar el primer instalador encontrado
        msi_path = msi_files[0]
        print(f"[WinFsp Installer] Instalando desde: {msi_path}")
        
        # Verificar que el archivo existe
        if not os.path.exists(msi_path):
            print(f"[WinFsp Installer] ERROR: El archivo no existe: {msi_path}")
            return False
        
        # Instalar MSI con privilegios de administrador
        print("[WinFsp Installer] Iniciando instalación...")
        ok = run_msiexec_admin(msi_path)
        
        if not ok:
            print("[WinFsp Installer] La instalación falló o fue cancelada")
            return False
        
        # Esperar a que la instalación finalice completamente
        print("[WinFsp Installer] Esperando a que finalice la instalación...")
        time.sleep(8)
        
        # Verificar si se instaló correctamente
        installed = check_winfsp()
        if installed:
            print("[WinFsp Installer] ¡WinFsp instalado exitosamente!")
        else:
            print("[WinFsp Installer] WinFsp no se detectó después de la instalación")
        
        return installed
    
    except Exception as e:
        print(f"[WinFsp Installer] Excepción: {e}")
        import traceback
        traceback.print_exc()
        return False

# Importaciones de PyQt6 para las clases siguientes
from PyQt6.QtCore import QObject, pyqtSignal, QThread, QTimer, Qt
from PyQt6.QtWidgets import QApplication

class WinFspInstaller(QObject):
    """Worker en segundo plano para instalar WinFsp sin bloquear la UI"""

    finished = pyqtSignal(bool)

    def run(self):
        success = install_winfsp_silent()
        if success and not check_winfsp():
            success = False
        self.finished.emit(success)

def start_component_check(window, manual=False, force_install=False):
    """Verifica e instala componentes sin bloquear la UI"""

    if getattr(window, "_winfsp_thread", None) and window._winfsp_thread.isRunning():
        window.statusBar().showMessage(window.tr("status_installing_winfsp"), 5000)
        return

    if not manual and getattr(window, "_component_check_completed", False) and not force_install:
        return

    window.statusBar().showMessage(window.tr("status_checking_components"), 3000)

    if check_winfsp() and not force_install:
        window._component_check_completed = True
        window.statusBar().showMessage(window.tr("status_components_ready"), 5000)
        return

    window.statusBar().showMessage(window.tr("status_installing_winfsp"))

    installer = WinFspInstaller()
    thread = QThread()
    installer.moveToThread(thread)

    def finish(success):
        if success and check_winfsp():
            window._component_check_completed = True
            window.statusBar().showMessage(window.tr("status_install_finished"), 8000)
        elif success:
            window.statusBar().showMessage(window.tr("status_install_cancelled"), 8000)
        else:
            window.statusBar().showMessage(window.tr("status_install_failed"), 8000)

        if thread.isRunning():
            thread.quit()
            thread.wait()
        else:
            thread.wait(100)

        installer.deleteLater()
        thread.deleteLater()
        window._winfsp_installer = None
        window._winfsp_thread = None

    installer.finished.connect(finish)
    thread.started.connect(installer.run)

    window._winfsp_installer = installer
    window._winfsp_thread = thread
    window._winfsp_installer = installer
    window._winfsp_thread = thread
    thread.start()

def exception_hook(exctype, value, traceback_obj):
    """Global exception hook to catch unhandled errors"""
    import traceback
    traceback_str = ''.join(traceback.format_exception(exctype, value, traceback_obj))
    error_msg = f"Unhandled Exception: {value}\n{traceback_str}"
    print(error_msg)
    if 'logger' in globals() and logger:
        logger.critical(error_msg)
    else:
        # Fallback to file if logger not ready
        try:
            with open("crash_log.txt", "a") as f:
                f.write(f"\n[{import_datetime_now()}] {error_msg}\n")
        except:
            pass
    sys.__excepthook__(exctype, value, traceback_obj)

def import_datetime_now():
    from datetime import datetime
    return datetime.now()

sys.excepthook = exception_hook

def main():
    app = QApplication(sys.argv)

    preferences = load_user_preferences()

    translations = None
    try:
        from translations import Translations
        translations = Translations()
        translations.set_language(preferences.get("language", "es"))
    except Exception as exc:
        translations = None
        message = f"unable to load translations: {exc}"
        if LOGGING_AVAILABLE and logger:
            logger.warning("No fue posible cargar traducciones al iniciar: %s", exc)
        else:
            print(f"[app] Warning: {message}")

    def app_tr(key, fallback):
        if translations:
            try:
                return translations.get(key)
            except Exception:
                if LOGGING_AVAILABLE and logger:
                    logger.debug("Fallo al obtener traducción '%s', usando fallback.", key)
        return fallback

    # ===== OPTIMIZACIÓN 3: Mostrar splash mientras carga el resto =====
    splash = None
    try:
        from splash_screen import FastSplashScreen
        splash = FastSplashScreen(
            title=app_tr("splash_title", "Vultr Drive Desktop"),
            subtitle=app_tr("splash_subtitle", "Productividad conectada a la nube")
        )
        splash.show()
        app.processEvents()  # Forzar renderizado del splash
    except:
        pass  # Si falla el splash, continuar sin él

    def show_splash_message(key, fallback):
        if splash:
            splash.showMessage(app_tr(key, fallback), Qt.AlignmentFlag.AlignCenter, Qt.GlobalColor.white)
            app.processEvents()

    show_splash_message("splash_initializing", "Iniciando...")
    
    # ===== VERIFICAR E INSTALAR WINFSP AUTOMÁTICAMENTE =====
    winfsp_installed_during_startup = False
    if not check_winfsp():
        if LOGGING_AVAILABLE:
            logger.info("WinFsp no está instalado. Intentando instalación automática...")
        else:
            print("[VultrDrive] WinFsp no está instalado. Intentando instalación automática...")
        
        show_splash_message("splash_installing_winfsp", "Instalando componentes requeridos (WinFsp)...")
        
        # Intentar instalar WinFsp automáticamente
        success = install_winfsp_silent()
        
        if success:
            if LOGGING_AVAILABLE:
                logger.info("WinFsp instalado exitosamente")
            else:
                print("[VultrDrive] WinFsp instalado exitosamente")
            winfsp_installed_during_startup = True
            show_splash_message("splash_winfsp_installed", "WinFsp instalado correctamente")
        else:
            if LOGGING_AVAILABLE:
                logger.warning("No se pudo instalar WinFsp automáticamente")
            else:
                print("[VultrDrive] No se pudo instalar WinFsp automáticamente")
            show_splash_message("splash_continue_without_winfsp", "Continuando sin WinFsp (instalación pendiente)...")
    else:
        if LOGGING_AVAILABLE:
            logger.debug("WinFsp ya está instalado")
        else:
            print("[VultrDrive] WinFsp ya está instalado")
    
    # ===== OPTIMIZACIÓN 4: Cargar módulos pesados con feedback =====
    show_splash_message("splash_loading_interface", "Cargando interfaz...")
    
    from ui.main_window import MainWindow
    from theme_manager import ThemeManager
    
    # Initialize theme manager and translations
    show_splash_message("splash_configuring_theme", "Configurando tema...")
    
    theme_manager = ThemeManager()
    
    # Set user preferences
    theme_manager.set_theme(preferences.get("theme", "dark"))
    if translations:
        translations.set_language(preferences.get("language", "es"))
    
    # Apply theme
    app.setStyleSheet(theme_manager.get_current_stylesheet())

    # Create main window with theme manager and translations
    show_splash_message("splash_initializing", "Iniciando...")
    
    # Cerrar splash ANTES de crear MainWindow para evitar bloqueos
    show_splash_message("splash_loading_application", "Cargando aplicación...")
    
    try:
        window = MainWindow(theme_manager, translations, save_user_preferences)
        if hasattr(window, "set_winfsp_installer"):
            window.set_winfsp_installer(lambda: start_component_check(window, manual=True, force_install=True))
        window.trigger_component_check = lambda: start_component_check(window)
        window.manual_install_winfsp = lambda: start_component_check(window, manual=True, force_install=True)
        
        # ===== ENCRIPTACIÓN DESHABILITADA: No migrar configuraciones =====
        
        # Cerrar splash INMEDIATAMENTE antes de mostrar ventana
        if splash:
            try:
                splash.finish(window)
            except:
                pass
            try:
                splash.close()
            except:
                pass
            splash = None  # Limpiar referencia
            app.processEvents()  # Procesar eventos para cerrar splash
        
        window.show()
        app.processEvents()  # Asegurar que la ventana se muestre
        
        # Asegurar que el splash esté cerrado (por si acaso)
        QTimer.singleShot(100, lambda: app.processEvents())
    except Exception as e:
        # Si hay error al crear la ventana, cerrar splash de todas formas
        if splash:
            splash.close()
        if LOGGING_AVAILABLE:
            logger.error(f"Error crítico al inicializar MainWindow: {e}", exc_info=True)
        else:
            print(f"[VultrDrive] Error crítico al inicializar MainWindow: {e}")
        import traceback
        traceback.print_exc()
        # Mostrar error al usuario
        from PyQt6.QtWidgets import QMessageBox
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setWindowTitle(app_tr("error_start_title", "Error al Iniciar"))
        msg.setText(app_tr("error_start_message", "Error al inicializar la aplicación."))
        msg.setDetailedText(str(e))
        msg.exec()
        sys.exit(1)
    
    if LOGGING_AVAILABLE:
        logger.info("Aplicación iniciada correctamente")
    
    # ===== NOTIFICAR INSTALACIÓN DE WINFSP =====
    # Notificar si WinFsp se instaló durante el inicio
    if winfsp_installed_during_startup and hasattr(window, 'notification_manager') and window.notification_manager:
        QTimer.singleShot(2000, lambda: window.notification_manager.notify_winfsp_installed())
    
    # ===== OPTIMIZACIÓN 5: Ejecutar tareas en segundo plano DESPUÉS de mostrar ventana =====
    # Detectar y desmontar discos montados (sin bloquear la UI)
    def cleanup_mounted_drives():
        """Ejecutar en segundo plano después de mostrar ventana"""
        try:
            from rclone_manager import RcloneManager
            mounted = RcloneManager.detect_mounted_drives()
            if mounted:
                # Hay discos montados, desmontarlos silenciosamente
                RcloneManager.unmount_all_drives()
        except:
            pass  # Si falla, no importa, continuar normalmente
    
    # Ejecutar en 500ms (medio segundo después de mostrar ventana)
    QTimer.singleShot(500, cleanup_mounted_drives)

    # Verificar componentes sin bloquear la apertura
    QTimer.singleShot(800, lambda: start_component_check(window))
    
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
