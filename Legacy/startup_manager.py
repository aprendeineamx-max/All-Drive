"""
Gestor de Inicio Automático - VultrDrive Desktop
Permite configurar el programa para que se ejecute al iniciar Windows
"""

import os
import sys
import winreg
from pathlib import Path

class StartupManager:
    """
    Gestor para configurar inicio automático en Windows
    """
    
    # Clave del registro de Windows para inicio automático
    STARTUP_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
    APP_NAME = "VultrDriveDesktop"
    
    def __init__(self):
        self.exe_path = self._get_exe_path()
    
    def _get_exe_path(self) -> str:
        """Obtener ruta del ejecutable actual"""
        if getattr(sys, 'frozen', False):
            # Ejecutando desde ejecutable empaquetado
            return sys.executable
        else:
            # Ejecutando desde script Python
            # Crear comando para ejecutar el script
            python_exe = sys.executable
            script_path = os.path.abspath(sys.argv[0])
            return f'"{python_exe}" "{script_path}"'
    
    def is_enabled(self) -> bool:
        """
        Verificar si el inicio automático está habilitado
        
        Returns:
            True si está configurado para iniciar con Windows
        """
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                self.STARTUP_KEY,
                0,
                winreg.KEY_READ
            )
            
            try:
                value, _ = winreg.QueryValueEx(key, self.APP_NAME)
                winreg.CloseKey(key)
                return True
            except FileNotFoundError:
                winreg.CloseKey(key)
                return False
                
        except Exception as e:
            print(f"[StartupManager] Error checking startup status: {e}")
            return False
    
    def enable(self, minimized: bool = False) -> tuple[bool, str]:
        """
        Habilitar inicio automático con Windows
        
        Args:
            minimized: Si True, iniciar minimizado en bandeja
            
        Returns:
            (success, message)
        """
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                self.STARTUP_KEY,
                0,
                winreg.KEY_WRITE
            )
            
            # Comando a ejecutar al inicio
            command = self.exe_path
            if minimized:
                command += ' --minimized'
            
            winreg.SetValueEx(
                key,
                self.APP_NAME,
                0,
                winreg.REG_SZ,
                command
            )
            
            winreg.CloseKey(key)
            
            mode = "minimizado" if minimized else "normal"
            return True, f"Inicio automático activado (modo {mode})"
            
        except Exception as e:
            return False, f"Error al activar inicio automático: {str(e)}"
    
    def disable(self) -> tuple[bool, str]:
        """
        Deshabilitar inicio automático con Windows
        
        Returns:
            (success, message)
        """
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                self.STARTUP_KEY,
                0,
                winreg.KEY_WRITE
            )
            
            try:
                winreg.DeleteValue(key, self.APP_NAME)
                winreg.CloseKey(key)
                return True, "Inicio automático desactivado"
            except FileNotFoundError:
                winreg.CloseKey(key)
                return True, "Inicio automático ya estaba desactivado"
                
        except Exception as e:
            return False, f"Error al desactivar inicio automático: {str(e)}"
    
    def toggle(self, enable: bool, minimized: bool = False) -> tuple[bool, str]:
        """
        Activar o desactivar inicio automático
        
        Args:
            enable: True para activar, False para desactivar
            minimized: Si True y enable=True, iniciar minimizado
            
        Returns:
            (success, message)
        """
        if enable:
            return self.enable(minimized)
        else:
            return self.disable()


# Método alternativo usando carpeta de inicio (más simple pero menos flexible)
class StartupFolderManager:
    """
    Gestor alternativo usando la carpeta de inicio de Windows
    Método más simple pero no permite argumentos de línea de comandos
    """
    
    APP_NAME = "VultrDriveDesktop"
    
    def __init__(self):
        self.startup_folder = self._get_startup_folder()
        self.shortcut_path = os.path.join(self.startup_folder, f"{self.APP_NAME}.lnk")
        self.exe_path = self._get_exe_path()
    
    def _get_startup_folder(self) -> str:
        """Obtener ruta de la carpeta de inicio"""
        return os.path.join(
            os.environ['APPDATA'],
            'Microsoft',
            'Windows',
            'Start Menu',
            'Programs',
            'Startup'
        )
    
    def _get_exe_path(self) -> str:
        """Obtener ruta del ejecutable"""
        if getattr(sys, 'frozen', False):
            return sys.executable
        else:
            python_exe = sys.executable
            script_path = os.path.abspath(sys.argv[0])
            return script_path
    
    def is_enabled(self) -> bool:
        """Verificar si existe el acceso directo"""
        return os.path.exists(self.shortcut_path)
    
    def enable(self) -> tuple[bool, str]:
        """Crear acceso directo en carpeta de inicio"""
        try:
            import win32com.client
            
            shell = win32com.client.Dispatch("WScript.Shell")
            shortcut = shell.CreateShortCut(self.shortcut_path)
            shortcut.Targetpath = self.exe_path
            shortcut.WorkingDirectory = os.path.dirname(self.exe_path)
            shortcut.IconLocation = self.exe_path
            shortcut.save()
            
            return True, "Acceso directo creado en carpeta de inicio"
            
        except ImportError:
            return False, "Requiere pywin32 para crear accesos directos"
        except Exception as e:
            return False, f"Error al crear acceso directo: {str(e)}"
    
    def disable(self) -> tuple[bool, str]:
        """Eliminar acceso directo de carpeta de inicio"""
        try:
            if os.path.exists(self.shortcut_path):
                os.remove(self.shortcut_path)
                return True, "Acceso directo eliminado"
            else:
                return True, "Acceso directo no existía"
        except Exception as e:
            return False, f"Error al eliminar acceso directo: {str(e)}"


# Función de conveniencia
def get_startup_manager(use_registry: bool = True):
    """
    Obtener gestor de inicio automático
    
    Args:
        use_registry: Si True, usa registro (recomendado).
                     Si False, usa carpeta de inicio.
    
    Returns:
        StartupManager o StartupFolderManager
    """
    if use_registry:
        return StartupManager()
    else:
        return StartupFolderManager()


