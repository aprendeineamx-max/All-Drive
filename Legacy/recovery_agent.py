class PhoenixRecoveryAgent:
    def __init__(self):
        self.rclone_exe = "X:\\Program Files\\Phoenix\\rclone.exe"
        self.mount_point = "X:\\Mount\\Backups"
        self.config_path = "X:\\Program Files\\Phoenix\\rclone.conf"
        self.log_file = "X:\\PhoenixRecovery.log"
        self.bucket_name = "desktop-backups" # Simplification for POC
        self.colors = {
            "HEADER": "\033[95m",
            "OKBLUE": "\033[94m",
            "OKGREEN": "\033[92m",
            "WARNING": "\033[93m",
            "FAIL": "\033[91m",
            "ENDC": "\033[0m",
            "BOLD": "\033[1m"
        }
        # Enable VT100 emulation in Windows console
        os.system("")

    def log(self, message, level="INFO"):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        full_msg = f"[{timestamp}] [{level}] {message}"
        
        # Print to screen
        color = self.colors["OKBLUE"]
        if level == "ERROR": color = self.colors["FAIL"]
        elif level == "SUCCESS": color = self.colors["OKGREEN"]
        elif level == "WARN": color = self.colors["WARNING"]
        
        print(f"{color}{full_msg}{self.colors['ENDC']}")
        
        # Write to file
        with open(self.log_file, "a") as f:
            f.write(full_msg + "\n")

    def upload_logs(self):
        """Sube el log de recuperación a la nube para diagnóstico remoto"""
        self.log("Subiendo logs de diagnóstico a la nube...", "INFO")
        remote = f"vultr:{self.bucket_name}/logs/{os.environ.get('COMPUTERNAME')}_recovery.log"
        cmd = [self.rclone_exe, "copyto", self.log_file, remote, "--config", self.config_path]
        subprocess.run(cmd, capture_output=True)

    def disk_manager(self):
        """Gestor de Discos con DISKPART"""
        while True:
            self.clear_screen()
            print(f"{self.colors['BOLD']}=== GESTOR DE DISCOS (DISKPART WRAPPER) ==={self.colors['ENDC']}")
            print("1. Listar Discos")
            print("2. Limpiar Disco (CLEAN - Destructivo)")
            print("3. Inicializar Disco (GPT)")
            print("4. Volver")
            
            op = input("\nOpción: ")
            
            if op == "1":
                self._run_diskpart_script("list disk")
            elif op == "2":
                disk = input("Nº de Disco a LIMPIAR (ej: 0): ")
                if disk:
                    confirm = input(f"{self.colors['FAIL']}ESTO BORRARÁ TODO EN DISCO {disk}. ESCRIBE 'YES': {self.colors['ENDC']}")
                    if confirm == "YES":
                        self._run_diskpart_script(f"select disk {disk}\nclean")
                        self.log(f"Disco {disk} limpiado.", "WARN")
            elif op == "3":
                disk = input("Nº de Disco a Inicializar GPT (ej: 0): ")
                if disk:
                    self._run_diskpart_script(f"select disk {disk}\nconvert gpt")
                    self.log(f"Disco {disk} convertido a GPT.", "SUCCESS")
            elif op == "4":
                break
            input("Continuar...")

    def _run_diskpart_script(self, commands):
        script_file = "X:\\diskpart_scr.txt"
        with open(script_file, "w") as f:
            f.write(commands)
        
        print(f"\n{self.colors['OKBLUE']}Ejecutando DiskPart...{self.colors['ENDC']}")
        subprocess.run(["diskpart", "/s", script_file])

    def check_network(self):
        self.log("Verificando conectividad...", "INFO")
        try:
            res = subprocess.run(["ping", "-n", "1", "8.8.8.8"], capture_output=True)
            if res.returncode == 0:
                self.log("Conexión a Internet DETECTADA.", "SUCCESS")
                return True
            else:
                self.log("Sin conexión. Intentando iniciar red (wpeinit)...", "WARN")
                subprocess.run("wpeinit", shell=True)
                time.sleep(5)
                res = subprocess.run(["ping", "-n", "1", "8.8.8.8"], capture_output=True)
                if res.returncode == 0:
                     self.log("Conexión ESTABLECIDA.", "SUCCESS")
                     return True
                else:
                     self.log("Fallo al iniciar red. Verifica cable o drivers.", "ERROR")
                     return False
        except Exception as e:
            self.log(f"Error de red: {e}", "ERROR")
            return False

    def list_backups(self):
        self.log("Buscando versiones de backup disponibles...", "INFO")
        try:
            cmd = ["wbadmin", "get", "versions", f"-backupTarget:{self.mount_point}"]
            subprocess.run(cmd)
        except Exception as e:
            self.log(f"Error listando backups: {e}", "ERROR")

    # [Previous methods remain but updated with self.log calls...]
    # Re-implementing simplified main logic for brevity in this replacement
    
    def clear_screen(self):
        os.system('cls')

    def mount_cloud_backup(self):
        self.log("Montando almacenamiento de backups...", "INFO")
        if not os.path.exists(self.mount_point): os.makedirs(self.mount_point)
        
        # Check config
        if not os.path.exists(self.config_path):
             self.log("No se encontró rclone.conf", "ERROR")
             return

        cmd = [
            self.rclone_exe, "mount",
            f"vultr:{self.bucket_name}",
            self.mount_point,
            "--config", self.config_path,
            "--vfs-cache-mode", "writes",
            "--network-mode",
            "--no-auth-split"
        ]
        
        try:
            subprocess.Popen(cmd, creationflags=subprocess.CREATE_NEW_CONSOLE)
            self.log("Esperando montaje (10s)...", "INFO")
            time.sleep(10)
            if os.path.exists(self.mount_point):
                self.log("Backups detectados correctamente.", "SUCCESS")
                # Intentar subir log de éxito
                self.upload_logs()
            else:
                self.log("Montaje fallido o lento.", "WARN")
        except Exception as e:
            self.log(f"Error fatal montando: {e}", "ERROR")

    def run_restore_wizard(self):
        print(f"\n{self.colors['BOLD']}=== ASISTENTE DE RECUPERACIÓN ==={self.colors['ENDC']}")
        print("ADVERTENCIA: Esto sobrescribirá los datos del disco local.")
        confirm = input("Escribe 'DESTROY' para continuar: ")
        if confirm != "DESTROY": return

        version = input("Introduce el Version Identifier (ej: 03/31/2024-09:00): ")
        if not version: return

        cmd = [
            "wbadmin", "start", "sysrecovery",
            f"-version:{version}",
            f"-backupTarget:{self.mount_point}",
            "-restoreAllVolumes",
            "-noprompt"
        ]
        
        print(f"Comando: {' '.join(cmd)}")
        # subprocess.run(cmd)
        self.log("Simulación de restauración iniciada.", "WARN")
        self.upload_logs()

    def main_menu(self):
        while True:
            self.clear_screen()
            print(f"{self.colors['HEADER']}=== PHOENIX AGENT v2.0 (Deep Edition) ==={self.colors['ENDC']}")
            print(f"Host: {os.environ.get('COMPUTERNAME')}")
            print("---------------------------------------")
            print("1. Verificar Red")
            print("2. Montar Nube (Vultr S3)")
            print("3. Gestor de Discos (DiskPart)")
            print("4. Listar Backups")
            print("5. Iniciar Restauración (Bare Metal)")
            print("6. Subir Logs a la Nube")
            print("7. Consola de Emergencia")
            print("8. Reiniciar")
            
            op = input(f"\n{self.colors['BOLD']}Opción: {self.colors['ENDC']}")
            
            if op == "1": self.check_network()
            elif op == "2": self.mount_cloud_backup()
            elif op == "3": self.disk_manager()
            elif op == "4": self.list_backups()
            elif op == "5": self.run_restore_wizard()
            elif op == "6": self.upload_logs()
            elif op == "7": os.system("cmd.exe")
            elif op == "8": sys.exit(0)
            
            input("\nPresiona Enter para continuar...")

if __name__ == "__main__":
    agent = PhoenixRecoveryAgent()
    agent.main_menu()
