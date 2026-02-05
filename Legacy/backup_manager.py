import subprocess
import shutil
import os
import re
from datetime import datetime
from pathlib import Path

class BackupManager:
    def __init__(self):
        self.wbadmin_exe = "wbadmin" 
        self._check_wbadmin_path()

    def _check_wbadmin_path(self):
        """Intenta localizar wbadmin.exe"""
        path = shutil.which("wbadmin")
        if path:
            self.wbadmin_exe = path
        else:
            # Fallback común
            sys_native = os.path.join(os.environ.get("SystemRoot", "C:\\Windows"), "Sysnative", "wbadmin.exe")
            if os.path.exists(sys_native):
                self.wbadmin_exe = sys_native
            else:
                sys32 = os.path.join(os.environ.get("SystemRoot", "C:\\Windows"), "System32", "wbadmin.exe")
                if os.path.exists(sys32):
                    self.wbadmin_exe = sys32

    def check_prerequisites(self):
        """Verifica si wbadmin está funcional."""
        try:
            cmd = [self.wbadmin_exe, "get", "versions"]
            result = subprocess.run(cmd, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
            
            if result.returncode == 0:
                return True, "Windows Server Backup está listo."
            
            error_msg = result.stderr.strip()
            if "not recognized" in error_msg or "no se reconoce" in error_msg:
                return False, "La herramienta 'wbadmin' no se encuentra. ¿Está instalada la característica Windows Server Backup?"
            
            return True, "Windows Server Backup parece estar instalado (aunque no haya backups previos)."
            
        except FileNotFoundError:
            return False, "Ejecutable wbadmin no encontrado."
        except Exception as e:
            return False, f"Error verificando wbadmin: {str(e)}"

    def get_available_drives(self):
        """Retorna una lista de letras de unidad disponibles para Staging (excluyendo C:)."""
        drives = []
        # Usar wmic para obtener discos lógicos
        try:
            cmd = ["wmic", "logicaldisk", "get", "caption,description,freespace,size"]
            result = subprocess.run(cmd, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
            
            lines = result.stdout.strip().split('\n')
            for line in lines[1:]: # Skip header
                parts = line.split()
                if len(parts) >= 3:
                    # Caption is usually first (C:)
                    drive_letter = parts[0]
                    
                    # Filtrar C: (no se puede usar como destino de su propio backup imagewise fácilmente sin particionar)
                    if drive_letter.upper() == "C:":
                        continue
                        
                    # Calcular espacio libre GB
                    try:
                        free_bytes = int(parts[-2]) if len(parts) > 2 and parts[-2].isdigit() else 0
                        size_bytes = int(parts[-1]) if len(parts) > 1 and parts[-1].isdigit() else 0
                        
                        free_gb = round(free_bytes / (1024**3), 2)
                        total_gb = round(size_bytes / (1024**3), 2)
                        
                        drives.append({
                            "letter": drive_letter,
                            "label": f"{drive_letter} ({free_gb} GB libres / {total_gb} GB Total)",
                            "free_gb": free_gb
                        })
                    except:
                        pass
        except Exception as e:
            print(f"Error listando discos: {e}")
            
        return drives

    def start_bare_metal_backup(self, target_drive_letter, include_drives="C:"):
        """
        Inicia un backup Bare Metal (all critical volumes) hacia el target local.
        IMPORTANTE: wbadmin requiere target dedicado o carpeta compartida.
        Aquí intentaremos usar una carpeta en la unidad target si es local.
        """
        # Nota: wbadmin start backup -backupTarget:D: -include:C: -allCritical -quiet
        
        # Eliminar trailing backslash
        target = target_drive_letter.rstrip("\\")
        
        cmd = [
            self.wbadmin_exe, 
            "start", "backup",
            f"-backupTarget:{target}",
            f"-include:{include_drives}",
            "-allCritical", # Bare metal recovery capability
            "-vssFull", # Full backup resetting logs
            "-quiet" # No prompts
        ]
        
        print(f"Ejecutando backup: {' '.join(cmd)}")
        
        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            return True, "Backup iniciado", process
        except Exception as e:
            return False, f"Error iniciando backup: {str(e)}", None

    def get_backup_status(self):
        """Parsea la salida de 'wbadmin get status'."""
        try:
            cmd = [self.wbadmin_exe, "get", "status"]
            result = subprocess.run(cmd, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
            
            if result.returncode != 0:
                return "Inactivo"
                
            # Parse output typically like:
            # "The backup operation for volume C: is running."
            # "Bytes transferred: 100 MB"
            return result.stdout.strip()
        except:
            return "Error consultando estado"
