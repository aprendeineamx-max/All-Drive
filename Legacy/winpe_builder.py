import subprocess
import os
import shutil
import sys
import ctypes
from pathlib import Path
from datetime import datetime

class WinPEBuilder:
    def __init__(self, workspace_path="C:\\WinPE_Workspace"):
        self.workspace_path = Path(workspace_path)
        self.adk_path = self._find_adk_path()
        self.virtio_iso_url = "https://fedorapeople.org/groups/virt/virtio-win/direct-downloads/stable-virtio/virtio-win.iso"
        
    def _find_adk_path(self):
        """Intenta localizar el directorio de instalación del ADK."""
        # Comprobar ubicaciones estándar
        common_paths = [
            Path("C:\\Program Files (x86)\\Windows Kits\\10\\Assessment and Deployment Kit"),
            Path("C:\\Program Files (x86)\\Windows Kits\\11\\Assessment and Deployment Kit") # Si existe 11
        ]
        
        for p in common_paths:
            if p.exists() and (p / "Deployment Tools").exists():
                return p
        return None

    def check_prerequisites(self):
        """Verifica si las herramientas necesarias (copype, dism, oscdimg) están disponibles."""
        status = {
            "adk_installed": False,
            "winpe_addon": False,
            "dism": False,
            "oscdimg": False,
            "admin_rights": False
        }
        
        # 1. Check Admin Rights
        try:
            status["admin_rights"] = ctypes.windll.shell32.IsUserAnAdmin() != 0
        except:
            status["admin_rights"] = False

        # 2. Check DISM (Built-in usually)
        if shutil.which("dism"):
            status["dism"] = True
            
        # 3. Check ADK and specific tools
        if self.adk_path:
            status["adk_installed"] = True
            
            # Check for oscdimg (deployment tools)
            oscdimg = self.adk_path / "Deployment Tools" / "amd64" / "Oscdimg" / "oscdimg.exe"
            if oscdimg.exists():
                status["oscdimg"] = True
                
            # Check for copype (WinPE Add-on)
            # Usually in C:\Program Files (x86)\Windows Kits\10\Assessment and Deployment Kit\Windows Preinstallation Environment\copype.cmd
            # Note: WinPE addon is separate in newer ADK versions
            winpe_root = self.adk_path.parent / "Assessment and Deployment Kit" / "Windows Preinstallation Environment"
            if not winpe_root.exists():
                 # Try same folder (older ADK)
                 winpe_root = self.adk_path / "Windows Preinstallation Environment"
            
            copype = winpe_root / "copype.cmd"
            if copype.exists():
                status["winpe_addon"] = True
            else:
                # Búsqueda recursiva por si acaso
                found = list(self.adk_path.parent.glob("**/copype.cmd"))
                if found:
                    status["winpe_addon"] = True

        return status

    def install_adk_via_winget(self):
        """Intenta instalar el ADK y el WinPE Add-on usando winget."""
        try:
            # 1. ADK
            print("Instalando Windows ADK...")
            subprocess.run(["winget", "install", "--id", "Microsoft.WindowsADK", "-e", "--source", "winget", "--accept-package-agreements", "--accept-source-agreements"], check=True)
            
            # 2. WinPE Add-on
            print("Instalando WinPE Add-on...")
            subprocess.run(["winget", "install", "--id", "Microsoft.WindowsADK.WinPE", "-e", "--source", "winget", "--accept-package-agreements", "--accept-source-agreements"], check=True)
            
            # Refrescar path
            self.adk_path = self._find_adk_path()
            return True, "Instalación completada (es posible que requiera reinicio o re-login)."
        except subprocess.CalledProcessError as e:
            return False, f"Falló la instalación via winget: {e}"
        except FileNotFoundError:
            return False, "winget no encontrado en el sistema."

    def _inject_drivers(self, mount_dir, status_callback=None):
        """Descarga e inyecta drivers VirtIO"""
        import urllib.request
        
        iso_dest = self.workspace_path / "virtio-win.iso"
        driver_mount_point = self.workspace_path / "virtio_mount"
        
        # 1. Descargar
        if not iso_dest.exists():
            print(f"Descargando drivers desde {self.virtio_iso_url}...")
            # For simplicity, blocking download. In prod, use requests with stream.
            try:
                urllib.request.urlretrieve(self.virtio_iso_url, iso_dest)
            except Exception as e:
                print(f"Error descargando drivers: {e}")
                return # Skip drivers if download fails (warn user)

        # 2. Montar ISO de Drivers
        if not driver_mount_point.exists():
            driver_mount_point.mkdir()
            
        # Usar PowerShell para montar
        # Mount-DiskImage -ImagePath "..." -StorageType ISO
        powershell_cmd = f'Mount-DiskImage -ImagePath "{iso_dest}" -StorageType ISO -PassThru | Get-Volume | Select-Object -ExpandProperty DriveLetter'
        res = subprocess.run(["powershell", "-Command", powershell_cmd], capture_output=True, text=True)
        drive_letter = res.stdout.strip()
        
        if not drive_letter:
            print("No se pudo montar la ISO de drivers.")
            return

        driver_source = f"{drive_letter}:\\"
        
        # 3. Inyectar (NetKVM, viostor, vioscsi) para w10/w11
        # Rutas comunes en la ISO: \NetKVM\w10\amd64, \viostor\w10\amd64
        drivers_to_inject = [
            f"{driver_source}NetKVM\\w10\\amd64",
            f"{driver_source}viostor\\w10\\amd64",
            f"{driver_source}vioscsi\\w10\\amd64"
        ]
        
        for driver_path in drivers_to_inject:
            print(f"Inyectando driver: {driver_path}")
            # dism /Image:mount_dir /Add-Driver /Driver:path /ForceUnsigned
            cmd = f'dism /Image:"{mount_dir}" /Add-Driver /Driver:"{driver_path}" /ForceUnsigned'
            subprocess.run(cmd, shell=True, creationflags=subprocess.CREATE_NO_WINDOW)

        # 4. Desmontar
        subprocess.run(["powershell", "-Command", f'Dismount-DiskImage -ImagePath "{iso_dest}"'], creationflags=subprocess.CREATE_NO_WINDOW)

    def build_iso(self, output_iso_path, status_callback=None):
        """
        Orquesta la creación de la ISO.
        status_callback(str, int progress_percent)
        """
        def report(msg, pct):
            if status_callback: status_callback(msg, pct)
            print(f"[WinPE Builder] {msg}")

        # 0. Validaciones previas
        if not self.adk_path:
            raise Exception("ADK no encontrado")
        
        # Localizar scripts críticos
        copype_cmd = self._find_tool("copype.cmd")
        makewinpemedia_cmd = self._find_tool("MakeWinPEMedia.cmd")
        
        if not copype_cmd or not makewinpemedia_cmd:
             raise Exception("No se encontraron scripts de despliegue (copype/MakeWinPEMedia)")

        # 1. Limpiar Workspace anterior
        report("Limpiando espacio de trabajo...", 10)
        start_time = datetime.now()
        
        if self.workspace_path.exists():
            try:
                # Intentar limpiar mountpoints huerfanos primero
                subprocess.run(f"dism /Cleanup-Mountpoints", shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
                # Retry deletion logic could go here
                shutil.rmtree(self.workspace_path)
            except Exception as e:
                # A veces DISM deja locks, esperamos un poco o forzamos
                pass 

        # 2. Copype (Crear estructura base)
        report("Generando estructura base (copype)...", 20)
        cmd = f'"{copype_cmd}" amd64 "{self.workspace_path}"'
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
        if res.returncode != 0:
            raise Exception(f"Error en copype: {res.stderr}")

        # 3. Montar Imagen (boot.wim)
        report("Montando imagen WIM...", 30)
        mount_dir = self.workspace_path / "mount"
        wim_file = self.workspace_path / "media" / "sources" / "boot.wim"
        
        cmd_mount = f'dism /Mount-Image /ImageFile:"{wim_file}" /index:1 /MountDir:"{mount_dir}"'
        res = subprocess.run(cmd_mount, shell=True, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
        if res.returncode != 0:
            raise Exception(f"Error montando WIM: {res.stderr}")

        try:
            # 4. Inyectar Drivers (VirtIO)
            report("Inyectando drivers VirtIO (Descarga + Inject)...", 50)
            self._inject_drivers(mount_dir, status_callback)

            # 5. Instalar Agente de Recuperación (Nuestra App)
            report("Instalando Agente Phoenix...", 70)
            self._install_recovery_agent(mount_dir)

            # 6. Configuración de Inicio (startnet.cmd)
            self._configure_startup(mount_dir)

        except Exception as e:
            # Intentar desmontar si falla
            subprocess.run(f'dism /Unmount-Image /MountDir:"{mount_dir}" /Discard', shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
            raise e

        # 7. Desmontar y Guardar Cambios
        report("Desmontando y guardando cambios...", 80)
        cmd_unmount = f'dism /Unmount-Image /MountDir:"{mount_dir}" /Commit'
        res = subprocess.run(cmd_unmount, shell=True, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
        if res.returncode != 0:
            raise Exception(f"Error guardando WIM: {res.stderr}")

        # 8. Generar ISO
        report("Generando archivo ISO...", 90)
        cmd_iso = f'"{makewinpemedia_cmd}" /ISO "{self.workspace_path}" "{output_iso_path}"'
        res = subprocess.run(cmd_iso, shell=True, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
        if res.returncode != 0:
            raise Exception(f"Error generando ISO: {res.stderr}")
            
        report("¡Proceso completado con éxito!", 100)
        return True

    def _find_tool(self, name):
        """Busca recursivamente una herramienta en el directorio del ADK"""
        if not self.adk_path: return None
        # Buscar en el parent también (ADK estructura antigua vs nueva)
        search_roots = [self.adk_path, self.adk_path.parent]
        for root in search_roots:
             found = list(root.rglob(name))
             if found: return found[0]
        return None

    def _install_recovery_agent(self, mount_dir):
        """
        Instala Python compatible, Rclone y el Agente en la imagen WinPE.
        """
        import urllib.request
        import zipfile
        
        target_root = mount_dir / "Program Files" / "Phoenix"
        if not target_root.exists():
            target_root.mkdir(parents=True)
            
        print(f"Instalando Phoenix Recovery Stack en {target_root}...")

        # 1. Instalar Python Portable (Embeddable)
        python_zip_url = "https://www.python.org/ftp/python/3.11.5/python-3.11.5-embed-amd64.zip"
        python_zip_path = self.workspace_path / "python_embed.zip"
        
        if not python_zip_path.exists():
            print(f"Descargando Python Runtime ({python_zip_url})...")
            try:
                urllib.request.urlretrieve(python_zip_url, python_zip_path)
            except Exception as e:
                print(f"Error descargando Python: {e}")
                # Fallback: intentar copiar el del sistema si es portable (poco probable)
                pass

        if python_zip_path.exists():
            print("Extrayendo Python Runtime...")
            python_dir = target_root / "Python"
            with zipfile.ZipFile(python_zip_path, 'r') as zip_ref:
                zip_ref.extractall(python_dir)
                
            # Activar importación de módulos (descomentar pth)
            # En la versión embed, hay un archivo ._pth que limita sys.path.
            # A veces es necesario editarlo para permitir importar scripts locales.
            pth_files = list(python_dir.glob("*._pth"))
            if pth_files:
                pth_file = pth_files[0]
                content = pth_file.read_text()
                # Uncomment 'import site' to enable full power if needed
                content = content.replace("#import site", "import site")
                pth_file.write_text(content)

        # 2. Copiar rclone.exe (del host)
        # Asumimos que rclone está en el PATH o en la carpeta actual
        rclone_src = shutil.which("rclone")
        if not rclone_src:
            # Intentar buscar en directorios comunes
            search_paths = [Path("."), Path("bin"), Path("C:\\rclone"), target_root.parent]
            for p in search_paths:
                candidate = p / "rclone.exe"
                if candidate.exists():
                    rclone_src = candidate
                    break
        
        if rclone_src:
            print(f"Copiando Rclone ({rclone_src})...")
            shutil.copy2(rclone_src, target_root / "rclone.exe")
        else:
            print("⚠️ ADVERTENCIA: rclone.exe no encontrado. El agente podría fallar.")

        # 3. Copiar rclone.conf (del usuario actual)
        # C:\Users\Administrator\.config\rclone\rclone.conf
        rclone_conf_src = Path(os.path.expanduser("~")) / ".config" / "rclone" / "rclone.conf"
        if rclone_conf_src.exists():
            print("Inyectando configuración de nube (rclone.conf)...")
            shutil.copy2(rclone_conf_src, target_root / "rclone.conf")
        else:
             print("⚠️ No se encontró rclone.conf. El agente requerirá configuración manual.")

        # 4. Copiar Agente (recovery_agent.py)
        # Asumimos que está en el CWD
        agent_src = Path("recovery_agent.py").absolute()
        if agent_src.exists():
             shutil.copy2(agent_src, target_root / "recovery_agent.py")
        else:
             # Try absolute path based on __file__ if running from module
             agent_src = Path(__file__).parent / "recovery_agent.py"
             if agent_src.exists():
                 shutil.copy2(agent_src, target_root / "recovery_agent.py")
             else:
                 print("ERROR CRÍTICO: No se encuentra recovery_agent.py")

    def _configure_startup(self, mount_dir):
        """Modifica startnet.cmd para iniciar el agente"""
        startnet = mount_dir / "windows" / "system32" / "startnet.cmd"
        
        cmd_content = [
            "wpeinit",
            "@echo off",
            "cls",
            "echo ==================================================",
            "echo      Iniciando Entorno de Recuperación Phoenix     ",
            "echo ==================================================",
            "echo Cargando drivers...",
            "drvload X:\\Windows\\System32\\DriverStore\\FileRepository\\*.inf >nul 2>&1",
            "echo Iniciando Agente Python...",
            r'set PATH=%PATH%;X:\Program Files\Phoenix\Python;X:\Program Files\Phoenix',
            r'cd /d "X:\Program Files\Phoenix"',
            r'python.exe recovery_agent.py',
            "if %ERRORLEVEL% NEQ 0 (",
            "  echo El agente se cerro o fallo. Abriendo consola de emergencia...",
            "  cmd /k",
            ")",
            "cmd /k"
        ]
        
        with open(startnet, "w") as f:
            f.write("\n".join(cmd_content))
 
