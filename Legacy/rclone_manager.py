import os
import sys
import subprocess
import shutil  # Para compresión de carpetas
import configparser
import time
from pathlib import Path
import zipfile

# ===== MEJORA #48: Manejo de Errores Mejorado =====
try:
    from error_handler import handle_error, MountError, ConnectionError, PermissionError
    ERROR_HANDLING_AVAILABLE = True
except ImportError:
    ERROR_HANDLING_AVAILABLE = False
    MountError = Exception
    ConnectionError = Exception
    PermissionError = Exception

class RcloneManager:
    def __init__(self, config_manager):
        self.config_manager = config_manager
        
        # Detectar si estamos ejecutando desde PyInstaller
        if getattr(sys, 'frozen', False):
            # Ejecutando desde ejecutable empaquetado
            base_path = os.path.dirname(sys.executable)
        else:
            # Ejecutando desde script Python
            base_path = os.path.dirname(os.path.abspath(__file__))
        
        self.rclone_exe = os.path.join(base_path, "rclone.exe")
        self.rclone_config_dir = os.path.join(os.path.expanduser("~"), ".config", "rclone")
        self.rclone_config_file = os.path.join(self.rclone_config_dir, "rclone.conf")
        os.makedirs(self.rclone_config_dir, exist_ok=True)
        self.mount_process = None
    
    @staticmethod
    def detect_mounted_drives():
        """
        Detecta todas las unidades montadas por rclone en el sistema
        Retorna: lista de letras de unidad (ej: ['V', 'W'])
        """
        mounted_drives = []
        try:
            # Ejecutar comando tasklist para buscar procesos rclone
            result = subprocess.run(
                ['tasklist', '/FI', 'IMAGENAME eq rclone.exe', '/FO', 'CSV', '/NH'],
                capture_output=True,
                text=True,
                timeout=2
            )
            
            if 'rclone.exe' in result.stdout:
                # Hay procesos rclone activos, verificar qué unidades están montadas
                for letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
                    drive_path = f"{letter}:\\"
                    if os.path.exists(drive_path):
                        # Verificar si es un montaje de rclone
                        try:
                            # Intentar leer el volumen
                            result = subprocess.run(
                                ['cmd', '/c', 'vol', f'{letter}:'],
                                capture_output=True,
                                text=True,
                                timeout=1
                            )
                            # Si tiene "rclone" en el output, es un montaje de rclone
                            if 'rclone' in result.stdout.lower() or result.returncode != 0:
                                mounted_drives.append(letter)
                        except:
                            pass
        except Exception as e:
            pass
        
        return mounted_drives
    
    @staticmethod
    def unmount_all_drives():
        """
        Desmonta todas las unidades montadas por rclone
        Retorna: (success, message)
        """
        try:
            # Terminar todos los procesos rclone
            subprocess.run(
                ['taskkill', '/F', '/IM', 'rclone.exe'],
                capture_output=True,
                timeout=5
            )
            time.sleep(1)
            return True, "Todas las unidades desmontadas correctamente"
        except Exception as e:
            return False, f"Error al desmontar: {str(e)}"

    def create_rclone_config(self, profile_name):
        """Create or update rclone configuration for a profile"""
        config = self.config_manager.get_config(profile_name)
        if not config:
            return False

        rclone_config = configparser.ConfigParser()
        
        # Load existing config if it exists
        if os.path.exists(self.rclone_config_file):
            rclone_config.read(self.rclone_config_file)

        # Add or update the profile
        section_name = f"vultr_{profile_name}"
        if not rclone_config.has_section(section_name):
            rclone_config.add_section(section_name)

        rclone_config.set(section_name, 'type', 's3')
        rclone_config.set(section_name, 'provider', 'Other')
        rclone_config.set(section_name, 'access_key_id', config['access_key'])
        rclone_config.set(section_name, 'secret_access_key', config['secret_key'])
        rclone_config.set(section_name, 'endpoint', f"https://{config['host_base']}")
        rclone_config.set(section_name, 'acl', 'private')

        # Save configuration
        with open(self.rclone_config_file, 'w') as f:
            rclone_config.write(f)

        return section_name

    def _find_rclone_executable(self):
        """Busca el ejecutable de rclone en varias ubicaciones."""
        if getattr(sys, 'frozen', False):
            base_path = os.path.dirname(sys.executable)
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))
        
        search_paths = [
            os.path.join(base_path, "rclone.exe"),
            self.rclone_exe,
            os.path.join(base_path, "rclone-v1.71.2-windows-amd64", "rclone.exe"),
            os.path.join(os.path.dirname(base_path), "rclone.exe"),
            "rclone"
        ]
        
        for path in search_paths:
            if path != "rclone" and os.path.exists(path):
                return path
            elif path == "rclone":
                try:
                    subprocess.run([path, "version"], capture_output=True, timeout=2, creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0)
                    return path
                except:
                    pass
        return None

    def create_mega_config(self, name, user, password):
        """
        Crea una configuración de MEGA usando rclone config create para asegurar
        que la contraseña se guarde encriptada/oscurecida correctamente.
        """
        rclone_path = self._find_rclone_executable()
        if not rclone_path:
            return False, "Rclone no encontrado"
            
        # rclone config create NAME mega user=USER pass=PASS
        cmd = [
            rclone_path,
            "config",
            "create",
            name,
            "mega",
            f"user={user}",
            f"pass={password}",
            "--config", self.rclone_config_file,
            "--non-interactive"
        ]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
            )
            
            if result.returncode == 0:
                return True, f"Cuenta MEGA '{name}' agregada correctamente"
            else:
                return False, f"Error al crear config: {result.stderr}"
        except Exception as e:
            return False, f"Excepción al crear config: {str(e)}"

    def create_gcp_config(self, name, service_account_file):
        """
        Crea o actualiza una configuración de Google Cloud Storage en rclone.conf
        """
        config = configparser.ConfigParser()
        if os.path.exists(self.rclone_config_file):
            config.read(self.rclone_config_file)
            
        if not config.has_section(name):
            config.add_section(name)
            
        config.set(name, 'type', 'google cloud storage')
        config.set(name, 'service_account_file', service_account_file)
        config.set(name, 'object_acl', 'private')
        config.set(name, 'bucket_acl', 'private')
        
        with open(self.rclone_config_file, 'w') as f:
            config.write(f)
            
        return name

    def list_mega_profiles(self):
        """Lista todos los perfiles que sean de tipo mega en rclone.conf"""
        profiles = []
        if not os.path.exists(self.rclone_config_file):
            return profiles
            
        config = configparser.ConfigParser()
        config.read(self.rclone_config_file)
        
        for section in config.sections():
            if config.has_option(section, 'type') and config.get(section, 'type') == 'mega':
                profiles.append({
                    'name': section,
                    'user': config.get(section, 'user', fallback='Unknown')
                })
        return profiles

    def delete_rclone_profile(self, name):
        """Elimina un perfil del archivo de configuración"""
        rclone_path = self._find_rclone_executable()
        if not rclone_path:
            return False, "Rclone no encontrado"
            
        cmd = [
            rclone_path,
            "config",
            "delete",
            name,
            "--config", self.rclone_config_file
        ]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
            )
            if result.returncode == 0:
                return True, "Perfil eliminado"
            else:
                return False, f"Error al eliminar: {result.stderr}"
        except Exception as e:
            return False, str(e)

    def copy_file_to_remote(self, remote_name, local_path, remote_path="/"):
        """
        Copia un archivo local a un remoto usando rclone copy.
        
        Args:
            remote_name: Nombre del remoto en rclone.conf
            local_path: Ruta completa del archivo local
            remote_path: Carpeta destino en el remoto (default: raíz)
        """
        rclone_path = self._find_rclone_executable()
        if not rclone_path:
            return False, "Rclone no encontrado"
        
        # rclone copy /path/to/file remote:path
        cmd = [
            rclone_path,
            "copy",
            local_path,
            f"{remote_name}:{remote_path}",
            "--config", self.rclone_config_file,
            "-v"
        ]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
            )
            
            if result.returncode == 0:
                return True, "Archivo subido correctamente"
            else:
                return False, f"Error: {result.stderr}"
        except Exception as e:
            return False, f"Excepción: {str(e)}"

    def copy_folder_to_remote(self, remote_name, local_folder, remote_path="/"):
        """
        Copia una carpeta local completa a un remoto usando rclone copy.
        
        Args:
            remote_name: Nombre del remoto en rclone.conf
            local_folder: Ruta de la carpeta local
            remote_path: Carpeta destino en el remoto (default: raíz)
        """
        rclone_path = self._find_rclone_executable()
        if not rclone_path:
            return False, "Rclone no encontrado"
        
        folder_name = os.path.basename(local_folder)
        dest_path = f"{remote_path}/{folder_name}" if remote_path != "/" else folder_name
        
        cmd = [
            rclone_path,
            "copy",
            local_folder,
            f"{remote_name}:{dest_path}",
            "--config", self.rclone_config_file,
            "-v"
        ]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
            )
            
            if result.returncode == 0:
                return True, "Carpeta respaldada correctamente"
            else:
                return False, f"Error: {result.stderr}"
        except Exception as e:
            return False, f"Excepción: {str(e)}"

    def mount_drive(self, profile_name, drive_letter, bucket_name=None, plan_config=None):
        """Mount the storage as a network drive.
        
        Args:
            profile_name (str): Vultr profile name or MEGA profile name
            drive_letter (str): Drive letter (e.g., "Z")
            bucket_name (str, optional): Specific bucket to mount
            plan_config (dict, optional): Dictionary with Rclone performance flags
        """
        # Try to create config from Vultr config.json
        section_name = self.create_rclone_config(profile_name)
        
        # If not found in config.json, check if it exists directly in rclone.conf (e.g. MEGA)
        if not section_name:
            if os.path.exists(self.rclone_config_file):
                config = configparser.ConfigParser()
                config.read(self.rclone_config_file)
                if config.has_section(profile_name):
                    section_name = profile_name  # Use the profile name directly as section
        
        if not section_name:
            return False, "Profile not found", None

        # Check if drive letter is available
        drive_path = f"{drive_letter}:\\"
        if os.path.exists(drive_path):
            return False, f"Drive letter {drive_letter}: is already in use", None

        # Build mount path
        if bucket_name:
            remote_path = f"{section_name}:{bucket_name}"
        else:
            remote_path = f"{section_name}:"

        mount_point = f"{drive_letter}:"

        rclone_path = self._find_rclone_executable()
        
        if not rclone_path:
            return False, (
                "Rclone executable not found. Please ensure rclone.exe is in the same folder as the application."
            ), None

        # Base Application Log Path
        log_path = os.path.join(os.path.expanduser("~"), "Desktop", "rclone_debug.txt")

        # Configuración por defecto (Fallback "Alto Rendimiento Estable")
        params = {
            "vfs_cache_mode": "writes",
            "vfs_cache_max_age": "24h",
            "vfs_write_back": "5s",
            "transfers": "32",
            "checkers": "32",
            "tpslimit": "50",
            "tpslimit_burst": "20",
            "buffer_size": "64M",
            "vfs_read_chunk_size": "128M",
            "timeout": "10h",
            "contimeout": "10m",
            "dir_cache_time": "30m", # Default decente
            "poll_interval": "1m"
        }

        # Override con plan_config si existe
        if plan_config:
            # Mapear claves del plan a claves de params (son casi iguales pero aseguramos)
            # plan_config keys: transfers, checkers, tpslimit, tpslimit_burst, vfs_cache_mode, buffer_size, vfs_read_chunk_size, dir_cache_time, poll_interval, timeout, contimeout
            for key, value in plan_config.items():
                if value is not None and str(value).strip() != "":
                    params[key] = str(value)

        # Construir comando
        cmd = [
            rclone_path,
            "mount",
            remote_path,
            mount_point,
            "--vfs-cache-mode", params["vfs_cache_mode"],
            "--vfs-cache-max-age", params.get("vfs_cache_max_age", "24h"),
            "--vfs-write-back", params.get("vfs_write_back", "5s"),
            "--transfers", params["transfers"],
            "--checkers", params["checkers"],
            "--buffer-size", params["buffer_size"],
            "--vfs-read-chunk-size", params["vfs_read_chunk_size"],
            "--timeout", params["timeout"],
            "--contimeout", params.get("contimeout", "10m"),
            "--dir-cache-time", params.get("dir_cache_time", "30m"),
            "--poll-interval", params.get("poll_interval", "1m"),
            "--retries", "5",
            "--stats", "1m",
            "--no-modtime",
            "--no-checksum",
            "--volname", f"Vultr-{profile_name}",
            "--log-file", log_path,
            "--log-level", "DEBUG"
        ]

        # Añadir TPS Limits solo si son explícitos (0 = ilimitado)
        tps = params.get("tpslimit", "0")
        burst = params.get("tpslimit_burst", "0")
        
        if tps and tps != "0":
            cmd.extend(["--tpslimit", tps])
        if burst and burst != "0":
            cmd.extend(["--tpslimit-burst", burst])

        try:
            # Start the mount process in background for Windows
            # Use CREATE_NEW_PROCESS_GROUP to allow it to run independently
            self.mount_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
            )

            # Check if the process is still running
            time.sleep(2)
            if self.mount_process.poll() is None:
                # Wait up to 40 seconds for drive to appear
                for i in range(40):
                    try:
                        if os.path.exists(f"{drive_letter}:\\"):
                            return True, f"Montado exitosamente en {drive_letter}:", self.mount_process
                        try:
                            os.listdir(f"{drive_letter}:\\")
                            return True, f"Montado exitosamente en {drive_letter}:", self.mount_process
                        except:
                            pass
                    except:
                        pass
                    time.sleep(1)
                
                self.mount_process.terminate()
                
                log_path = os.path.join(os.path.expanduser("~"), "Desktop", "rclone_debug.txt")
                error_details = "No se generó log."
                if os.path.exists(log_path):
                    try:
                        with open(log_path, "r", encoding="utf-8") as f:
                            lines = f.readlines()
                            error_details = "".join(lines[-15:])
                    except:
                        pass

                return False, (
                    f"No se pudo montar la unidad {drive_letter}:\\n\\n"
                    f"El proceso inició pero la unidad no apareció después de 40 segundos.\\n\\n"
                    f"DETALLES DEL ERROR (rclone log):\\n{error_details}\\n\\n"
                    f"Intenta reducir los parámetros agresivos."
                ), None

            else:
                # Process exited immediately

                stdout, stderr = self.mount_process.communicate()
                error_msg = stderr.decode('utf-8', errors='ignore') if stderr else "Error desconocido"
                
                # Detectar si es error de WinFsp
                if "winfsp" in error_msg.lower() or "cannot find winfsp" in error_msg.lower() or "cgofuse" in error_msg.lower():
                    return False, (
                        "⚠️ WinFsp no está instalado correctamente en este sistema.\n\n"
                        "SOLUCIÓN RÁPIDA:\n"
                        "1. Cierra esta aplicación\n"
                        "2. Ejecuta: INSTALAR_WINFSP.bat (en la carpeta del programa)\n"
                        "3. Reinicia Windows (importante)\n"
                        "4. Vuelve a abrir VultrDriveDesktop\n\n"
                        "O descarga manualmente:\n"
                        "https://winfsp.dev/rel/\n"
                        "Archivo: winfsp-2.0.23075.msi\n\n"
                        "WinFsp es REQUERIDO para montar unidades en Windows.\n"
                        "Es gratuito y de código abierto."
                    ), None
                
                return False, f"Error al montar: {error_msg}", None
                
        except FileNotFoundError as e:
            if ERROR_HANDLING_AVAILABLE:
                error = MountError(
                    f"Ejecutable de Rclone no encontrado en: {rclone_path}",
                    suggestion="Verifica que rclone.exe esté en la carpeta del programa",
                    original_error=e
                )
                handle_error(error)
            return False, f"Error: Ejecutable no encontrado: {e}", None
                
        except Exception as e:
            return False, f"Error al montar: {str(e)}", None

    def unmount_drive(self, drive_letter):
        """Unmount the drive usando net use (específico para esa letra)"""
        try:
            import time
            drive_path = f"{drive_letter}:"
            
            # Primero intentar con net use para desmontar SOLO esa letra
            result = subprocess.run(
                ['net', 'use', drive_path, '/delete', '/yes'],
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            time.sleep(1.0)
            
            # Verificar si se desmontó
            vol_result = subprocess.run(
                ['cmd', '/c', 'vol', drive_path],
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            if vol_result.returncode != 0:
                # Se desmontó exitosamente
                if self.mount_process:
                    self.mount_process = None
                return True, f"Unidad {drive_letter}: desmontada exitosamente"
            
            # Si net use no funcionó, terminar el proceso rclone
            if self.mount_process:
                try:
                    self.mount_process.terminate()
                    self.mount_process.wait(timeout=2)
                    self.mount_process = None
                    time.sleep(0.5)
                except:
                    pass
            
            # Verificar nuevamente
            vol_result2 = subprocess.run(
                ['cmd', '/c', 'vol', drive_path],
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            if vol_result2.returncode != 0:
                return True, f"Unidad {drive_letter}: desmontada exitosamente"
            else:
                return False, f"No se pudo desmontar la unidad {drive_letter}.\\nIntenta cerrar todos los archivos abiertos desde esta unidad."
                
        except Exception as e:
            return False, f"Error al desmontar: {str(e)}"

    def is_mounted(self):
        """Check if a drive is currently mounted"""
        return self.mount_process is not None and self.mount_process.poll() is None

    def list_buckets_rclone(self, profile_name):
        """List all buckets using rclone"""
        section_name = self.create_rclone_config(profile_name)
        if not section_name:
             if os.path.exists(self.rclone_config_file):
                config = configparser.ConfigParser()
                config.read(self.rclone_config_file)
                if config.has_section(profile_name):
                    section_name = profile_name
        
        if not section_name:
            return []

        cmd = [self.rclone_exe, "lsd", f"{section_name}:"]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                buckets = []
                for line in result.stdout.strip().split('\n'):
                    if line:
                        parts = line.split()
                        if len(parts) >= 5:
                            bucket_name = parts[-1]
                            buckets.append(bucket_name)
                return buckets
            return []
        except Exception as e:
            print(f"Error listing buckets: {e}")
            return []

    def compress_folder(self, source_folder, output_path=None):
        """
        Comprime una carpeta local en un archivo ZIP. (Version robusta con streaming y timestamp safe)
        """
        try:
            source_path = Path(source_folder)
            if not source_path.exists():
                return False, f"La carpeta origen no existe: {source_folder}"

            if output_path is None:
                temp_dir = os.path.join(os.environ.get('TEMP', os.path.expanduser('~')), 'VultrDrive_Backups')
                os.makedirs(temp_dir, exist_ok=True)
                folder_name = source_path.name
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                # ZIP extension must be explicit in this custom implementation
                zip_path = os.path.join(temp_dir, f"{folder_name}_{timestamp}.zip")
            else:
                zip_path = output_path if output_path.lower().endswith('.zip') else output_path + '.zip'

            # Implementación custom con zipfile
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED, allowZip64=True) as zf:
                for root, dirs, files in os.walk(str(source_path)):
                    # Guardar root folder structure también? 
                    # shutil.make_archive guarda root_dir como base.
                    # Haremos equivalente: items dentro de source_folder quedan en root del zip.
                    
                    for file in files:
                        full_path = os.path.join(root, file)
                        # Path relativo al source_folder
                        rel_path = os.path.relpath(full_path, str(source_path))
                        # Si queremos preservar la carpeta contenedora, usar source_path.parent
                        # Pero standard es contenido.
                        
                        try:
                            # Crear ZipInfo desde archivo para preservar permisos y fechas
                            zinfo = zipfile.ZipInfo.from_file(full_path, rel_path)
                            
                            # FIX CRITICO: Timestamps pre-1980 causan crash
                            if zinfo.date_time < (1980, 1, 1, 0, 0, 0):
                                zinfo.date_time = (1980, 1, 1, 0, 0, 0)
                            
                            # Streaming copy: file -> zip (sin leer todo a RAM)
                            with open(full_path, 'rb') as src, zf.open(zinfo, 'w') as dst:
                                shutil.copyfileobj(src, dst)
                                
                        except Exception as e:
                            print(f"[Compress] Omitiendo {file}: {e}")
                            # Omitir archivo problemático y seguir con el resto
            
            return True, zip_path
        except Exception as e:
            return False, str(e)

    def upload_file(self, profile_name, local_file, bucket_name, remote_filename=None, progress_callback=None, **kwargs):
        """
        Sube un archivo único usando rclone copyto con optimizaciones S3 (multipart).
        Soporta **kwargs para ajustar el rendimiento al vuelo (Ultra/Stability).
        """
        try:
            rclone_path = self._find_rclone_executable()
            if not rclone_path:
                 return False, "Error: Ejecutable de rclone no encontrado"
            section_name = self.create_rclone_config(profile_name)

            if not remote_filename:
                remote_filename = os.path.basename(local_file)
            
            remote_path = f"{section_name}:{bucket_name}/{remote_filename}"
            
            # Construir comando base
            cmd = [
                rclone_path,
                "copyto",
                local_file,
                remote_path,
                "--config", self.rclone_config_file,
                "--stats", "1s",
                "--stats-one-line",
                "--log-level", "INFO",
                "--rc", # Habilitar control remoto para Live Tuning
                "--rc-no-auth" # Simplificar acceso local
            ]

            # ===== OPTIMIZACIONES DE VELOCIDAD S3 =====
            # Para archivos únicos, 'transfers' no ayuda mucho, pero s3-upload-concurrency SI.
            # Convertimos el plan 'transfers' (ej 320) en concurrency para el multipart.
            
            transfers_val = int(kwargs.get('transfers', 4))
            
            # S3 Upload Concurrency: Define cuántas partes del MISMO archivo se suben a la vez.
            # Rclone default es 4. Para Ultra, queremos saturar.
            s3_concurrency = transfers_val if transfers_val < 64 else 64 # Cap seguro de 64 hilos por archivo
            
            cmd.extend(["--s3-upload-concurrency", str(s3_concurrency)])
            
            # Chunk Size: Más grande = menos overhead requests, mejor para archivos grandes.
            # Default 5M. Subimos a 64M o 128M en modo Ultra.
            if transfers_val > 100: # Modo Ultra
                cmd.extend(["--s3-chunk-size", "128M"])
            elif transfers_val > 10: # Modo Balanced
                cmd.extend(["--s3-chunk-size", "32M"])
            
            # Otros flags pass-through
            if 'checkers' in kwargs:
                cmd.extend(["--checkers", str(kwargs['checkers'])])
            if 'tpslimit' in kwargs and int(kwargs['tpslimit']) > 0:
                cmd.extend(["--tpslimit", str(kwargs['tpslimit'])])
            
            # Debug log
            print(f"DEBUG: upload_file flags: concurrency={s3_concurrency}")

            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
            )
            
            # Leer progreso
            while True:
                line = process.stderr.readline()
                if not line and process.poll() is not None:
                    break
                
                if line and progress_callback:
                    # Si callback devuelve False, ABORTAR
                    continue_upload = progress_callback(line.strip())
                    if continue_upload is False:
                        process.kill()
                        return False, "Cancelado por el usuario"

            if process.returncode == 0:
                return True, "Subida completada"
            else:
                return False, "Error en rclone copyto"

        except Exception as e:
            return False, str(e)

    def sync_folder_parallel(self, profile_name, local_folder, bucket_name, remote_folder=None, progress_callback=None, **kwargs):
        """
        Sincroniza carpeta local con bucket usando rclone sync multipart.
        Soporta kwargs para planes de rendimiento (transfers, checkers, etc)
        """
        try:
            rclone_path = self._find_rclone_executable()
            if not rclone_path:
                 return False, "Error: Ejecutable de rclone no encontrado"
            
            section_name = self.create_rclone_config(profile_name)

            folder_name = os.path.basename(os.path.normpath(local_folder))
            if not remote_folder:
                 remote_folder = folder_name
            
            # Destino: nombre_seccion:bucket/nombre_carpeta
            remote_dest = f"{section_name}:{bucket_name}/{remote_folder}"
            
            # Defaults extremos pero configurables
            transfers = str(kwargs.get('transfers', '32'))
            checkers = str(kwargs.get('checkers', '32'))
            tpslimit = str(kwargs.get('tpslimit', '0')) # 0 = Unlimited
            burst = str(kwargs.get('tpslimit_burst', '0'))

            cmd = [
                rclone_path,
                "copy",
                local_folder,
                remote_dest,
                "--config", self.rclone_config_file,
                "--transfers", transfers,
                "--checkers", checkers,
                "--stats", "1s",
                "--stats-one-line",
                "--log-level", "INFO"
            ]

            if tpslimit and tpslimit != '0':
                cmd.extend(["--tpslimit", tpslimit])
            
            if burst and burst != '0':
                cmd.extend(["--tpslimit-burst", burst])

            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
            )
            
            while True:
                line = process.stderr.readline()
                if not line and process.poll() is not None:
                    break
                if line and progress_callback:
                    progress_callback(line.strip())

            if process.returncode == 0:
                return True, "Sincronización paralela completada"
            else:
                return False, "Error en rclone copy paralelo"

        except Exception as e:
            return False, str(e)
