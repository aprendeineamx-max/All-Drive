"""
Azure Disk Downloader Tab - Gestión de Discos de Azure
Permite autenticarse con Azure mediante múltiples métodos y descargar discos administrados.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QGroupBox, QFormLayout, QTabWidget, QTextEdit, QTableWidget,
    QTableWidgetItem, QHeaderView, QFileDialog, QMessageBox, QProgressBar,
    QScrollArea, QApplication, QFrame, QComboBox, QInputDialog, QStackedWidget,
    QCheckBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QDesktopServices
from PyQt6.QtCore import QUrl
import json
import os

from config_manager import ConfigManager
try:
    from s3_handler import S3Handler
    S3_AVAILABLE = True
except ImportError:
    S3_AVAILABLE = False

# Transfer Manager for multi-download queue
try:
    from transfer_manager import get_transfer_manager, TransferType, TransferStatus
    from ui.transfer_queue_widget import TransferQueueWidget
    TRANSFER_MANAGER_AVAILABLE = True
except ImportError:
    TRANSFER_MANAGER_AVAILABLE = False


# ============================================================================
# WORKERS PARA AUTENTICACIÓN Y OPERACIONES
# ============================================================================

class GCPWorker(QThread):
    finished = pyqtSignal(bool, object, str)
    
    def __init__(self, func, *args, **kwargs):
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs
        
    def run(self):
        try:
            result = self.func(*self.args, **self.kwargs)
            self.finished.emit(True, result, "Operation successful")
        except Exception as e:
            self.finished.emit(False, None, str(e))

class InteractiveLoginWorker(QThread):
    """Worker para login interactivo con navegador"""
    finished = pyqtSignal(bool, str, object)  # success, message, credential
    
    def __init__(self, subscription_id):
        super().__init__()
        self.subscription_id = subscription_id
    
    def run(self):
        try:
            from azure.identity import InteractiveBrowserCredential
            from azure.mgmt.compute import ComputeManagementClient
            
            credential = InteractiveBrowserCredential()
            
            # Probar la conexión
            compute_client = ComputeManagementClient(credential, self.subscription_id)
            _ = list(compute_client.disks.list())
            
            self.finished.emit(True, "✅ Autenticación exitosa con tu cuenta Microsoft", credential)
        except Exception as e:
            self.finished.emit(False, f"❌ Error: {str(e)}", None)


class DeviceCodeLoginWorker(QThread):
    """Worker para login con código de dispositivo"""
    code_received = pyqtSignal(str, str)  # user_code, verification_uri
    finished = pyqtSignal(bool, str, object)  # success, message, credential
    
    def __init__(self, subscription_id):
        super().__init__()
        self.subscription_id = subscription_id
    
    def run(self):
        try:
            from azure.identity import DeviceCodeCredential
            from azure.mgmt.compute import ComputeManagementClient
            
            def callback(verification_uri, user_code, expires_on):
                self.code_received.emit(user_code, verification_uri)
            
            credential = DeviceCodeCredential(prompt_callback=callback)
            
            # Probar la conexión
            compute_client = ComputeManagementClient(credential, self.subscription_id)
            _ = list(compute_client.disks.list())
            
            self.finished.emit(True, "✅ Autenticación exitosa con código de dispositivo", credential)
        except Exception as e:
            self.finished.emit(False, f"❌ Error: {str(e)}", None)


class AzureCliLoginWorker(QThread):
    """Worker para login usando Azure CLI"""
    finished = pyqtSignal(bool, str, object)  # success, message, credential
    
    def __init__(self, subscription_id):
        super().__init__()
        self.subscription_id = subscription_id
    
    def run(self):
        try:
            from azure.identity import AzureCliCredential
            from azure.mgmt.compute import ComputeManagementClient
            
            credential = AzureCliCredential()
            
            # Probar la conexión
            compute_client = ComputeManagementClient(credential, self.subscription_id)
            _ = list(compute_client.disks.list())
            
            self.finished.emit(True, "✅ Autenticación exitosa usando Azure CLI", credential)
        except Exception as e:
            if "Azure CLI not found" in str(e) or "az" in str(e).lower():
                self.finished.emit(False, "❌ Azure CLI no está instalado. Instálalo desde: https://aka.ms/installazurecli", None)
            elif "Please run 'az login'" in str(e):
                self.finished.emit(False, "❌ No has iniciado sesión en Azure CLI. Ejecuta 'az login' en una terminal.", None)
            else:
                self.finished.emit(False, f"❌ Error: {str(e)}", None)


class ServicePrincipalLoginWorker(QThread):
    """Worker para login con Service Principal"""
    finished = pyqtSignal(bool, str, object)  # success, message, credential
    
    def __init__(self, tenant_id, client_id, client_secret, subscription_id):
        super().__init__()
        self.tenant_id = tenant_id
        self.client_id = client_id
        self.client_secret = client_secret
        self.subscription_id = subscription_id
    
    def run(self):
        try:
            from azure.identity import ClientSecretCredential
            from azure.mgmt.compute import ComputeManagementClient
            
            credential = ClientSecretCredential(
                tenant_id=self.tenant_id,
                client_id=self.client_id,
                client_secret=self.client_secret
            )
            
            compute_client = ComputeManagementClient(credential, self.subscription_id)
            _ = list(compute_client.disks.list())
            
            self.finished.emit(True, "✅ Autenticación exitosa con Service Principal", credential)
        except Exception as e:
            self.finished.emit(False, f"❌ Error: {str(e)}", None)


class ListDisksWorker(QThread):
    """Worker para listar discos usando cualquier credential"""
    finished = pyqtSignal(bool, list, str)
    
    def __init__(self, credential, subscription_id):
        super().__init__()
        self.credential = credential
        self.subscription_id = subscription_id
    
    def run(self):
        try:
            from azure.mgmt.compute import ComputeManagementClient
            from azure.mgmt.resource import ResourceManagementClient
            
            compute_client = ComputeManagementClient(self.credential, self.subscription_id)
            resource_client = ResourceManagementClient(self.credential, self.subscription_id)
            
            # Debug: List Resource Groups first
            rgs = list(resource_client.resource_groups.list())
            rg_names = [rg.name for rg in rgs]
            
            disks = []
            # Try to list all disks in subscription
            all_disks = list(compute_client.disks.list())
            
            for disk in all_disks:
                disks.append({
                    'name': disk.name,
                    'location': disk.location,
                    'size_gb': disk.disk_size_gb,
                    'state': disk.disk_state,
                    'resource_group': disk.id.split('/')[4],
                    'id': disk.id
                })
            
            if not disks:
                debug_msg = f"⚠️ No se encontraron discos.\n\nDebug Info:\nSubscription: {self.subscription_id}\nResource Groups encontrados ({len(rgs)}): {', '.join(rg_names[:5])}..."
                self.finished.emit(True, [], debug_msg)
            else:
                self.finished.emit(True, disks, f"✅ Se encontraron {len(disks)} discos")
        except Exception as e:
            self.finished.emit(False, [], f"❌ Error listando discos: {str(e)}")


class DownloadDiskWorker(QThread):
    """Worker para descargar disco usando cualquier credential - Soporta resume"""
    progress = pyqtSignal(int, str)
    progress_bytes = pyqtSignal(int, int)  # bytes_downloaded, total_bytes
    finished = pyqtSignal(bool, str)
    
    def __init__(self, credential, subscription_id, resource_group, disk_name, output_path,
                 sas_url=None, start_byte=0, transfer_id=None):
        super().__init__()
        self.credential = credential
        self.subscription_id = subscription_id
        self.resource_group = resource_group
        self.disk_name = disk_name
        self.output_path = output_path
        self.sas_url = sas_url  # Pre-existing SAS for resume
        self.start_byte = start_byte
        self.transfer_id = transfer_id
        self._should_stop = False
    
    def stop(self):
        """Flag to gracefully stop the download"""
        self._should_stop = True
    
    def run(self):
        try:
            from azure.mgmt.compute import ComputeManagementClient
            import requests
            import os
            
            # If we don't have a SAS URL, get one
            if not self.sas_url:
                self.progress.emit(10, "Conectando con Azure...")
                
                compute_client = ComputeManagementClient(self.credential, self.subscription_id)
                
                self.progress.emit(20, "Solicitando acceso al disco...")
                
                grant_access_result = compute_client.disks.begin_grant_access(
                    resource_group_name=self.resource_group,
                    disk_name=self.disk_name,
                    grant_access_data={'access': 'Read', 'duration_in_seconds': 86400}  # 24 hours for large files
                ).result()
                
                self.sas_url = grant_access_result.access_sas
            
            self.progress.emit(30, "Iniciando descarga...")
            
            # Check if we're resuming an existing file
            existing_size = 0
            if os.path.exists(self.output_path) and self.start_byte > 0:
                existing_size = os.path.getsize(self.output_path)
                if existing_size > 0:
                    self.start_byte = existing_size
            
            # Prepare headers for range request
            headers = {}
            if self.start_byte > 0:
                headers['Range'] = f'bytes={self.start_byte}-'
                self.progress.emit(30, f"Reanudando desde {self.start_byte / (1024**3):.2f} GB...")
            
            response = requests.get(self.sas_url, stream=True, headers=headers)
            response.raise_for_status()
            
            # Handle partial content (206) or full content (200)
            if response.status_code == 206:
                # Partial content - we're resuming
                content_range = response.headers.get('content-range', '')
                if '/' in content_range:
                    total_size = int(content_range.split('/')[-1])
                else:
                    total_size = int(response.headers.get('content-length', 0)) + self.start_byte
            else:
                # Full content - start from beginning
                total_size = int(response.headers.get('content-length', 0))
                self.start_byte = 0
            
            downloaded = self.start_byte
            
            # Open file in append mode if resuming, write mode if starting fresh
            mode = 'ab' if self.start_byte > 0 else 'wb'
            
            with open(self.output_path, mode) as f:
                for chunk in response.iter_content(chunk_size=8192 * 1024):  # 8MB chunks
                    if self._should_stop:
                        self.finished.emit(False, "⏸️ Descarga pausada")
                        return
                    
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        # Emit byte-level progress for TransferManager
                        self.progress_bytes.emit(downloaded, total_size)
                        
                        if total_size > 0:
                            pct = int((downloaded / total_size) * 70) + 30
                            gb_dl = downloaded / (1024**3)
                            gb_total = total_size / (1024**3)
                            self.progress.emit(pct, f"Descargando: {gb_dl:.2f} / {gb_total:.2f} GB")
            
            # Only revoke access if we obtained a new SAS
            if self.credential:
                self.progress.emit(95, "Revocando acceso...")
                try:
                    compute_client = ComputeManagementClient(self.credential, self.subscription_id)
                    compute_client.disks.begin_revoke_access(
                        resource_group_name=self.resource_group,
                        disk_name=self.disk_name
                    ).result()
                except:
                    pass  # Ignore revoke errors
            
            self.progress.emit(100, "¡Completado!")
            self.finished.emit(True, f"✅ Disco descargado en:\n{self.output_path}")
        except Exception as e:
            self.finished.emit(False, f"❌ Error: {str(e)}")




class AzureToGCPTransferWorker(QThread):
    """Worker para transferir disco de Azure a GCP (Streaming)"""
    progress = pyqtSignal(int, str)
    finished = pyqtSignal(bool, str)
    
    def __init__(self, azure_credential, subscription_id, resource_group, disk_name, 
                 gcp_bucket_name, gcp_blob_name=None):
        super().__init__()
        self.cred = azure_credential
        self.sub_id = subscription_id
        self.rg = resource_group
        self.disk_name = disk_name
        self.bucket_name = gcp_bucket_name
        self.blob_name = gcp_blob_name or f"{disk_name}.vhd"
        self._is_running = True
        
    def run(self):
        try:
            from azure.mgmt.compute import ComputeManagementClient
            from google.cloud import storage
            import requests
            import time
            
            # 1. Obtener SAS de Azure
            self.progress.emit(5, "Conectando con Azure...")
            compute_client = ComputeManagementClient(self.cred, self.sub_id)
            
            self.progress.emit(10, "Generando SAS de lectura...")
            grant_access_result = compute_client.disks.begin_grant_access(
                resource_group_name=self.rg,
                disk_name=self.disk_name,
                grant_access_data={'access': 'Read', 'duration_in_seconds': 86400}
            ).result()
            sas_url = grant_access_result.access_sas
            
            # 2. Preparar subida a GCP
            self.progress.emit(15, "Conectando con Google Cloud...")
            # Asumimos que GOOGLE_APPLICATION_CREDENTIALS ya está seteado por la UI
            storage_client = storage.Client()
            bucket = storage_client.bucket(self.bucket_name)
            blob = bucket.blob(self.blob_name)
            
            # 3. Streaming Upload
            self.progress.emit(20, "Iniciando transferencia (Streaming)...")
            
            # Obtener stream de Azure
            response = requests.get(sas_url, stream=True)
            response.raise_for_status()
            total_size = int(response.headers.get('content-length', 0))
            
            # Clase adaptador para reportar progreso durante la lectura del stream
            class ProgressReader:
                def __init__(self, stream, total, progress_signal, worker):
                    self.stream = stream
                    self.total = total
                    self.downloaded = 0
                    self.signal = progress_signal
                    self.worker = worker
                    self.last_emit = 0

                def read(self, size=-1):
                    if not self.worker._is_running:
                        raise Exception("Transferencia cancelada por usuario")
                        
                    data = self.stream.read(size)
                    if data:
                        self.downloaded += len(data)
                        # Emitir cada 1% o cada 2MB para no saturar
                        if self.total > 0:
                            pct = int((self.downloaded / self.total) * 100)
                            # Mapear 20-95% en la barra global
                            ui_pct = 20 + int(pct * 0.75)
                            
                            current_time = time.time()
                            if current_time - self.last_emit > 0.5: # Throttle emits
                                gb_dl = self.downloaded / (1024**3)
                                gb_tot = self.total / (1024**3)
                                self.signal.emit(ui_pct, f"Transfiriendo: {gb_dl:.2f} / {gb_tot:.2f} GB ({pct}%)")
                                self.last_emit = current_time
                    return data
                
                def tell(self):
                    """Return current position in stream (required by GCP upload)"""
                    return self.downloaded
                
                def seek(self, pos, whence=0):
                    """Seek is not supported for streaming, but GCP may call it"""
                    if pos == 0 and whence == 0:
                        # GCP may try to seek to start - we can't, but we can ignore
                        pass
                    # For streaming, we just ignore seeks
                    return self.downloaded
                
                def readable(self):
                    return True
                
                def seekable(self):
                    return False


            adapter = ProgressReader(response.raw, total_size, self.progress, self)
            
            # Subir usando upload_from_file que consumirá el adaptador
            # blob.upload_from_file espera un objeto file-like y hace read()
            blob.upload_from_file(adapter, content_type="application/octet-stream")
            
            # 4. Finalizar
            self.progress.emit(95, "Revocando SAS en Azure...")
            compute_client.disks.begin_revoke_access(
                resource_group_name=self.rg,
                disk_name=self.disk_name
            ).wait()
            
            self.progress.emit(100, "¡Transferencia Completada!")
            self.finished.emit(True, f"✅ Disco transferido a GCP:\nBucket: {self.bucket_name}\nArchivo: {self.blob_name}")
            
        except Exception as e:
            self.finished.emit(False, f"❌ Error: {str(e)}")
            
    def stop(self):
        self._is_running = False



class AzureTransferWorker(QThread):
    """Worker para transferir disco entre cuentas usando SAS"""
    progress = pyqtSignal(int, str)
    finished = pyqtSignal(bool, str)
    
    def __init__(self, source_credential, source_sub, source_rg, disk_name, 
                 target_credential, target_sub, target_rg, target_location):
        super().__init__()
        self.src_cred = source_credential
        self.src_sub = source_sub
        self.src_rg = source_rg
        self.disk_name = disk_name
        
        self.tgt_cred = target_credential
        self.tgt_sub = target_sub
        self.tgt_rg = target_rg
        self.tgt_loc = target_location
        
    def run(self):
        try:
            from azure.mgmt.compute import ComputeManagementClient
            from azure.mgmt.compute.models import Disk, DiskCreationData, CreationData
            import time
            
            # 1. Clientes
            src_client = ComputeManagementClient(self.src_cred, self.src_sub)
            tgt_client = ComputeManagementClient(self.tgt_cred, self.tgt_sub)
            
            # 2. Obtener disco fuente para detalles (tamaño, sku, etc)
            self.progress.emit(5, "Obteniendo detalles del disco origen...")
            source_disk = src_client.disks.get(self.src_rg, self.disk_name)
            
            # 3. Generar SAS en origen
            self.progress.emit(10, "Generando SAS de lectura en origen...")
            sas_result = src_client.disks.begin_grant_access(
                resource_group_name=self.src_rg,
                disk_name=self.disk_name,
                grant_access_data={'access': 'Read', 'duration_in_seconds': 86400} # 24h para asegurar
            ).result()
            sas_uri = sas_result.access_sas
            
            try:
                # 4. Crear disco en destino
                self.progress.emit(20, f"Iniciando creación en destino ({self.tgt_rg})...")
                
                poller = tgt_client.disks.begin_create_or_update(
                    resource_group_name=self.tgt_rg,
                    disk_name=self.disk_name, # Mismo nombre
                    disk=Disk(
                        location=self.tgt_loc,
                        creation_data=CreationData(
                            create_option='Import',
                            source_uri=sas_uri
                        ),
                        disk_size_gb=source_disk.disk_size_gb,
                        sku=source_disk.sku
                    )
                )
                
                # 5. Monitorear progreso
                # El poller espera a que la operación de CREACIÓN termine, 
                # pero para 'Import', la copia de datos puede seguir en background.
                # Sin embargo, begin_create_or_update usualmente retorna cuando está listo para usarse o en estado terminal.
                
                while not poller.done():
                    self.progress.emit(30, "Creando recurso en destino...")
                    time.sleep(2)
                
                tgt_disk_resource = poller.result()
                
                # 6. Esperar a que el estado sea 'Succeeded' y la copia termine
                # A veces 'Import' tarda después de crear el recurso
                self.progress.emit(50, "Esperando finalización de copia de datos...")
                
                while True:
                    d = tgt_client.disks.get(self.tgt_rg, self.disk_name)
                    if d.provisioning_state == 'Succeeded':
                        break
                    elif d.provisioning_state == 'Failed':
                        raise Exception("La provisión del disco en destino falló.")
                    
                    # Calcular progreso si está disponible en completion_percent
                    # Nota: completion_percent no siempre está poblado para managed disks imports, pero intentamos
                    pct = 50
                    if hasattr(d, 'completion_percent') and d.completion_percent:
                        pct = 50 + (d.completion_percent / 2)
                    
                    self.progress.emit(int(pct), f"Copiando datos... estado: {d.provisioning_state}")
                    time.sleep(5)
                
                self.progress.emit(100, "Transferencia completada")
                self.finished.emit(True, f"✅ Disco transferido exitosamente a:\nSub: {self.tgt_sub}\nRG: {self.tgt_rg}")

            finally:
                # 7. Siempre revocar SAS en origen al terminar o fallar
                self.progress.emit(95, "Revocando acceso en origen...")
                try:
                    src_client.disks.begin_revoke_access(self.src_rg, self.disk_name).wait()
                except Exception as e:
                    print(f"Error revocando SAS: {e}")

        except Exception as e:
            self.finished.emit(False, f"❌ Error en transferencia: {str(e)}")


class GetResourceGroupsWorker(QThread):
    """Obtiene Resource Groups de una suscripción"""
    finished = pyqtSignal(list, str)
    
    def __init__(self, credential, subscription_id):
        super().__init__()
        self.credential = credential
        self.subscription_id = subscription_id
        
    def run(self):
        try:
            from azure.mgmt.resource import ResourceManagementClient
            client = ResourceManagementClient(self.credential, self.subscription_id)
            rgs = [rg.name for rg in client.resource_groups.list()]
            self.finished.emit(rgs, "")
        except Exception as e:
            self.finished.emit([], str(e))


class S3UploadWorker(QThread):
    """Worker para subir archivos a S3"""
    progress = pyqtSignal(int, str)
    finished = pyqtSignal(bool, str)
    
    def __init__(self, s3_handler, bucket_name, file_path, object_name=None):
        super().__init__()
        self.s3 = s3_handler
        self.bucket = bucket_name
        self.file_path = file_path
        self.object_name = object_name or os.path.basename(file_path)
        
    def run(self):
        try:
            self.progress.emit(10, f"Iniciando subida a {self.bucket}...")
            # La subida es sincrónica en s3_handler, pero estamos en un thread
            success = self.s3.upload_file(self.bucket, self.file_path, self.object_name)
            
            if success:
                self.progress.emit(100, "Subida completada")
                self.finished.emit(True, f"✅ Archivo subido a Vultr S3:\nBucket: {self.bucket}\nArchivo: {self.object_name}")
            else:
                self.finished.emit(False, "❌ Falló la subida a S3 (ver consola)")
        except Exception as e:
            self.finished.emit(False, f"❌ Error subiendo a S3: {str(e)}")


# ============================================================================
# PESTAÑA PRINCIPAL DE AZURE
# ============================================================================

class AzureTab(QWidget):
    """Pestaña principal para gestión de Azure Disks"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent
        self.active_credential = None
        self.subscription_id = None
        self.current_disks = []
        self.auth_method = None
        self.profiles = {}
        self.current_profile_name = None
        
        self.init_ui()
        self.load_profiles()
    
    def init_ui(self):
        # Layout principal de la pestaña (contendrá el scroll)
        if self.layout() is None:
            main_layout = QVBoxLayout(self)
            main_layout.setContentsMargins(0, 0, 0, 0)
            main_layout.setSpacing(0)
        else:
            main_layout = self.layout()

        # Scroll Area para hacer la pestaña responsiva
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("background-color: transparent;")

        # Widget contenedor del contenido
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Header
        header = QLabel("🔷 Gestor de Discos de Azure")
        header.setStyleSheet("font-size: 18px; font-weight: bold; color: #0078D4;")
        layout.addWidget(header)
        
        # Estado de conexión
        self.connection_status = QLabel("⚪ No conectado")
        self.connection_status.setStyleSheet("font-size: 12px; color: #7f8c8d; padding: 5px;")
        layout.addWidget(self.connection_status)
        
        # Selector de Perfiles
        profile_group = QGroupBox("👤 Perfil de Azure")
        profile_layout = QHBoxLayout()
        
        self.profile_combo = QComboBox()
        self.profile_combo.currentIndexChanged.connect(self.on_profile_changed)
        profile_layout.addWidget(QLabel("Seleccionar Perfil:"))
        profile_layout.addWidget(self.profile_combo)
        
        new_profile_btn = QPushButton("➕ Nuevo")
        new_profile_btn.clicked.connect(self.create_new_profile)
        new_profile_btn.setStyleSheet("background-color: #27ae60; color: white; padding: 5px 10px;")
        profile_layout.addWidget(new_profile_btn)
        
        delete_profile_btn = QPushButton("🗑️ Borrar")
        delete_profile_btn.clicked.connect(self.delete_current_profile)
        delete_profile_btn.setStyleSheet("background-color: #c0392b; color: white; padding: 5px 10px;")
        profile_layout.addWidget(delete_profile_btn)
        
        profile_group.setLayout(profile_layout)
        layout.addWidget(profile_group)
        
        # Pestañas principales
        self.tabs = QTabWidget()
        self.tabs.addTab(self.create_auth_tab(), "🔐 Autenticación")
        self.tabs.addTab(self.create_disks_tab(), "💿 Mis Discos")
        self.tabs.addTab(self.create_help_tab(), "❓ Ayuda")
        
        layout.addWidget(self.tabs)
        
        # === Transfer Queue Widget (múltiples descargas) ===
        if TRANSFER_MANAGER_AVAILABLE:
            self.transfer_queue = TransferQueueWidget()
            self.transfer_queue.setMaximumHeight(300)
            self.transfer_queue.resume_requested.connect(self.on_resume_transfer)
            layout.addWidget(self.transfer_queue)
            
            # Initialize transfer manager reference
            self.transfer_manager = get_transfer_manager()
        else:
            self.transfer_queue = None
            self.transfer_manager = None
        
        # Finalizar setup del scroll
        scroll.setWidget(content_widget)
        main_layout.addWidget(scroll)
    
    def create_link_button_row(self, text, url, parent_layout=None):
        """Crea un row con botón de abrir enlace y copiar enlace"""
        row = QHBoxLayout()
        
        open_btn = QPushButton(f"🔗 {text}")
        open_btn.setStyleSheet("background-color: #0078D4; color: white; padding: 8px;")
        open_btn.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(url)))
        row.addWidget(open_btn)
        
        copy_btn = QPushButton("📋 Copiar")
        copy_btn.setFixedWidth(80)
        copy_btn.setStyleSheet("padding: 8px;")
        copy_btn.clicked.connect(lambda: self.copy_to_clipboard(url))
        row.addWidget(copy_btn)
        
        if parent_layout:
            parent_layout.addLayout(row)
        return row
    
    def copy_to_clipboard(self, text):
        """Copia texto al portapapeles"""
        QApplication.clipboard().setText(text)
        if self.main_window and hasattr(self.main_window, 'statusBar'):
            self.main_window.statusBar().showMessage("✅ Enlace copiado al portapapeles", 3000)
    
    def create_auth_tab(self):
        """Pestaña de autenticación con múltiples métodos"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Subscription ID (común para todos los métodos)
        sub_group = QGroupBox("📋 Subscription ID (Requerido para todos los métodos)")
        sub_layout = QHBoxLayout()
        
        self.subscription_input = QLineEdit()
        self.subscription_input.setPlaceholderText("ea0991ac-97e9-48a1-b880-224a0fee751a")
        sub_layout.addWidget(QLabel("Subscription ID:"))
        sub_layout.addWidget(self.subscription_input)
        
        # Botón para obtener Subscription ID con copiar
        sub_url = "https://portal.azure.com/#view/Microsoft_Azure_Billing/SubscriptionsBlade"
        sub_help_btn = QPushButton("🔗 Obtener")
        sub_help_btn.setToolTip("Abrir Azure Portal para obtener tu Subscription ID")
        sub_help_btn.setStyleSheet("background-color: #0078D4; color: white; padding: 5px 10px;")
        sub_help_btn.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(sub_url)))
        sub_layout.addWidget(sub_help_btn)
        
        sub_copy_btn = QPushButton("📋")
        sub_copy_btn.setToolTip("Copiar enlace")
        sub_copy_btn.setFixedWidth(35)
        sub_copy_btn.clicked.connect(lambda: self.copy_to_clipboard(sub_url))
        sub_layout.addWidget(sub_copy_btn)
        
        sub_group.setLayout(sub_layout)
        layout.addWidget(sub_group)
        
        # Sub-pestañas de métodos de autenticación
        self.auth_tabs = QTabWidget()
        self.auth_tabs.addTab(self.create_interactive_auth(), "🌐 Login Interactivo")
        self.auth_tabs.addTab(self.create_device_code_auth(), "📱 Código de Dispositivo")
        self.auth_tabs.addTab(self.create_cli_auth(), "💻 Azure CLI")
        self.auth_tabs.addTab(self.create_service_principal_auth(), "🔑 Service Principal")
        
        layout.addWidget(self.auth_tabs)
        
        return widget
    
    def create_interactive_auth(self):
        """Login interactivo con navegador"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Descripción con colores para tema oscuro
        desc = QLabel(
            "<b style='color: #90CAF9;'>⭐ MÉTODO RECOMENDADO</b><br><br>"
            "<span style='color: #E0E0E0;'>Este método abre tu navegador y te permite iniciar sesión con tu cuenta de Microsoft.</span><br>"
            "<span style='color: #E0E0E0;'>No necesitas crear App Registration ni copiar credenciales.</span><br><br>"
            "<b style='color: #90CAF9;'>Requisitos:</b><br>"
            "<span style='color: #FFCC80;'>• Tu cuenta debe tener el rol 'Data Operator for Managed Disks' asignado</span>"
        )
        desc.setWordWrap(True)
        desc.setStyleSheet("background-color: #1a237e; padding: 15px; border-radius: 8px; border: 1px solid #3949ab;")
        layout.addWidget(desc)
        
        # Botón para asignar rol con copiar
        role_url = "https://portal.azure.com/#view/Microsoft_Azure_Billing/SubscriptionsBlade"
        role_row = QHBoxLayout()
        role_btn = QPushButton("🔗 Asignar Rol en Azure Portal")
        role_btn.setStyleSheet("background-color: #5c6bc0; color: white; padding: 8px;")
        role_btn.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(role_url)))
        role_row.addWidget(role_btn)
        
        role_copy_btn = QPushButton("📋 Copiar")
        role_copy_btn.setFixedWidth(80)
        role_copy_btn.clicked.connect(lambda: self.copy_to_clipboard(role_url))
        role_row.addWidget(role_copy_btn)
        layout.addLayout(role_row)
        
        # Botón de login
        self.interactive_btn = QPushButton("🚀 Conectar con mi Cuenta Microsoft")
        self.interactive_btn.setStyleSheet("""
            QPushButton {
                background-color: #0078D4;
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 15px 30px;
                border-radius: 8px;
            }
            QPushButton:hover { background-color: #005a9e; }
            QPushButton:disabled { background-color: #7f8c8d; }
        """)
        self.interactive_btn.clicked.connect(self.do_interactive_login)
        layout.addWidget(self.interactive_btn)
        
        self.interactive_status = QLabel("")
        layout.addWidget(self.interactive_status)
        
        layout.addStretch()
        return widget
    
    def create_device_code_auth(self):
        """Login con código de dispositivo"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        desc = QLabel(
            "<b style='color: #FFB74D;'>📱 Código de Dispositivo</b><br><br>"
            "<span style='color: #E0E0E0;'>Útil si el navegador no puede abrirse automáticamente.</span><br>"
            "<span style='color: #E0E0E0;'>Se mostrará un código que debes ingresar en una página web.</span>"
        )
        desc.setWordWrap(True)
        desc.setStyleSheet("background-color: #4a3000; padding: 15px; border-radius: 8px; border: 1px solid #ff9800;")
        layout.addWidget(desc)
        
        self.device_code_btn = QPushButton("📱 Obtener Código de Dispositivo")
        self.device_code_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff9800;
                color: white;
                font-weight: bold;
                padding: 12px;
                border-radius: 5px;
            }
            QPushButton:hover { background-color: #f57c00; }
        """)
        self.device_code_btn.clicked.connect(self.do_device_code_login)
        layout.addWidget(self.device_code_btn)
        
        # Área para mostrar el código
        self.device_code_display = QGroupBox("Código de Autenticación")
        dc_layout = QVBoxLayout()
        
        self.device_code_label = QLabel("Haz clic en el botón para obtener un código")
        self.device_code_label.setStyleSheet("font-size: 14px;")
        dc_layout.addWidget(self.device_code_label)
        
        self.device_code_copy_btn = QPushButton("📋 Copiar Código")
        self.device_code_copy_btn.setVisible(False)
        self.device_code_copy_btn.clicked.connect(self.copy_device_code)
        dc_layout.addWidget(self.device_code_copy_btn)
        
        self.device_code_display.setLayout(dc_layout)
        layout.addWidget(self.device_code_display)
        
        self.device_code_status = QLabel("")
        layout.addWidget(self.device_code_status)
        
        layout.addStretch()
        return widget
    
    def create_cli_auth(self):
        """Login usando Azure CLI"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        desc = QLabel(
            "<b style='color: #81C784;'>💻 Azure CLI</b><br><br>"
            "<span style='color: #E0E0E0;'>Usa las credenciales de Azure CLI si ya has ejecutado 'az login'.</span><br><br>"
            "<b style='color: #81C784;'>Pasos:</b><br>"
            "<span style='color: #E0E0E0;'>1. Instala Azure CLI</span><br>"
            "<span style='color: #E0E0E0;'>2. Abre una terminal y ejecuta: </span><span style='color: #FFCC80;'>az login</span><br>"
            "<span style='color: #E0E0E0;'>3. Vuelve aquí y haz clic en Conectar</span>"
        )
        desc.setWordWrap(True)
        desc.setStyleSheet("background-color: #1b3d1b; padding: 15px; border-radius: 8px; border: 1px solid #4caf50;")
        layout.addWidget(desc)
        
        # Botón para instalar Azure CLI con copiar
        cli_url = "https://aka.ms/installazurecli"
        cli_row = QHBoxLayout()
        cli_install_btn = QPushButton("🔗 Descargar Azure CLI")
        cli_install_btn.setStyleSheet("background-color: #2e7d32; color: white; padding: 8px;")
        cli_install_btn.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(cli_url)))
        cli_row.addWidget(cli_install_btn)
        
        cli_copy_btn = QPushButton("📋 Copiar")
        cli_copy_btn.setFixedWidth(80)
        cli_copy_btn.clicked.connect(lambda: self.copy_to_clipboard(cli_url))
        cli_row.addWidget(cli_copy_btn)
        layout.addLayout(cli_row)
        
        self.cli_btn = QPushButton("💻 Conectar usando Azure CLI")
        self.cli_btn.setStyleSheet("""
            QPushButton {
                background-color: #4caf50;
                color: white;
                font-weight: bold;
                padding: 12px;
                border-radius: 5px;
            }
            QPushButton:hover { background-color: #388e3c; }
        """)
        self.cli_btn.clicked.connect(self.do_cli_login)
        layout.addWidget(self.cli_btn)
        
        self.cli_status = QLabel("")
        layout.addWidget(self.cli_status)
        
        layout.addStretch()
        return widget
    
    def create_service_principal_auth(self):
        """Login con Service Principal (método avanzado)"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        desc = QLabel(
            "<b style='color: #CE93D8;'>🔑 Service Principal (Avanzado)</b><br><br>"
            "<span style='color: #E0E0E0;'>Método tradicional usando App Registration.</span><br>"
            "<span style='color: #E0E0E0;'>Útil para automatización y scripts sin interacción de usuario.</span>"
        )
        desc.setWordWrap(True)
        desc.setStyleSheet("background-color: #2d1b36; padding: 15px; border-radius: 8px; border: 1px solid #9c27b0;")
        layout.addWidget(desc)
        
        # Formulario con botones de ayuda
        form_group = QGroupBox("Credenciales del Service Principal")
        form_layout = QVBoxLayout()
        
        # Tenant ID
        tenant_url = "https://portal.azure.com/#view/Microsoft_AAD_IAM/ActiveDirectoryMenuBlade/~/RegisteredApps"
        tenant_row = QHBoxLayout()
        self.sp_tenant_input = QLineEdit()
        self.sp_tenant_input.setPlaceholderText("67e6c48a-6fd6-4b8a-85c2-e9ef4bb109f7")
        tenant_row.addWidget(QLabel("Tenant ID:"))
        tenant_row.addWidget(self.sp_tenant_input)
        tenant_help = QPushButton("🔗")
        tenant_help.setToolTip("Ver en App Registrations")
        tenant_help.setFixedWidth(35)
        tenant_help.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(tenant_url)))
        tenant_row.addWidget(tenant_help)
        tenant_copy = QPushButton("📋")
        tenant_copy.setToolTip("Copiar enlace")
        tenant_copy.setFixedWidth(35)
        tenant_copy.clicked.connect(lambda: self.copy_to_clipboard(tenant_url))
        tenant_row.addWidget(tenant_copy)
        form_layout.addLayout(tenant_row)
        
        # Client ID
        client_url = "https://portal.azure.com/#view/Microsoft_AAD_IAM/ActiveDirectoryMenuBlade/~/RegisteredApps"
        client_row = QHBoxLayout()
        self.sp_client_id_input = QLineEdit()
        self.sp_client_id_input.setPlaceholderText("8a90e14c-5e2c-4e80-ac04-8c9f8a371c59")
        client_row.addWidget(QLabel("Client ID:"))
        client_row.addWidget(self.sp_client_id_input)
        client_help = QPushButton("🔗")
        client_help.setToolTip("Ver en App Registrations")
        client_help.setFixedWidth(35)
        client_help.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(client_url)))
        client_row.addWidget(client_help)
        client_copy = QPushButton("📋")
        client_copy.setToolTip("Copiar enlace")
        client_copy.setFixedWidth(35)
        client_copy.clicked.connect(lambda: self.copy_to_clipboard(client_url))
        client_row.addWidget(client_copy)
        form_layout.addLayout(client_row)
        
        # Client Secret
        secret_url = "https://portal.azure.com/#view/Microsoft_AAD_IAM/ActiveDirectoryMenuBlade/~/RegisteredApps"
        secret_row = QHBoxLayout()
        self.sp_client_secret_input = QLineEdit()
        self.sp_client_secret_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.sp_client_secret_input.setPlaceholderText("Dkq8Q~~CGFxPL...")
        secret_row.addWidget(QLabel("Client Secret:"))
        secret_row.addWidget(self.sp_client_secret_input)
        secret_help = QPushButton("🔗")
        secret_help.setToolTip("Crear en Certificates & Secrets de tu App")
        secret_help.setFixedWidth(35)
        secret_help.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(secret_url)))
        secret_row.addWidget(secret_help)
        secret_copy = QPushButton("📋")
        secret_copy.setToolTip("Copiar enlace")
        secret_copy.setFixedWidth(35)
        secret_copy.clicked.connect(lambda: self.copy_to_clipboard(secret_url))
        secret_row.addWidget(secret_copy)
        form_layout.addLayout(secret_row)
        
        form_group.setLayout(form_layout)
        layout.addWidget(form_group)
        
        # Botones
        btn_layout = QHBoxLayout()
        
        self.sp_connect_btn = QPushButton("🔑 Conectar con Service Principal")
        self.sp_connect_btn.setStyleSheet("""
            QPushButton {
                background-color: #9c27b0;
                color: white;
                font-weight: bold;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover { background-color: #7b1fa2; }
        """)
        self.sp_connect_btn.clicked.connect(self.do_service_principal_login)
        btn_layout.addWidget(self.sp_connect_btn)
        
        save_btn = QPushButton("💾 Guardar Credenciales")
        save_btn.clicked.connect(self.save_sp_credentials)
        btn_layout.addWidget(save_btn)
        
        layout.addLayout(btn_layout)
        
        self.sp_status = QLabel("")
        layout.addWidget(self.sp_status)
        
        layout.addStretch()
        
        # Cargar credenciales guardadas
        self.load_sp_credentials()
        
        return widget
    
    def create_disks_tab(self):
        """Pestaña de discos"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        refresh_btn = QPushButton("🔄 Actualizar Lista de Discos")
        refresh_btn.setStyleSheet("background-color: #27ae60; color: white; padding: 8px;")
        refresh_btn.clicked.connect(self.refresh_disks)
        layout.addWidget(refresh_btn)
        
        self.disks_table = QTableWidget()
        self.disks_table.setColumnCount(6)
        self.disks_table.setHorizontalHeaderLabels([
            "Nombre", "Ubicación", "Tamaño (GB)", "Estado", "Grupo de Recursos", "Acciones"
        ])
        self.disks_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.disks_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        self.disks_table.setAlternatingRowColors(True)
        self.disks_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        self.disks_table.setAlternatingRowColors(True)
        layout.addWidget(self.disks_table)

        # Configuración de Descarga
        dest_group = QGroupBox("📂 Configuración de Descarga")
        dest_layout = QVBoxLayout()
        
        # Selector de Destino
        dest_row = QHBoxLayout()
        dest_row.addWidget(QLabel("Destino:"))
        self.dest_combo = QComboBox()
        self.dest_combo.addItems(["💾 Local File System", "☁️ Vultr Object Storage (S3)", "🔄 Transferir a otra cuenta Azure", "☁️ Google Cloud Platform (GCP)"])
        self.dest_combo.currentIndexChanged.connect(self.on_destination_changed)
        dest_row.addWidget(self.dest_combo)
        dest_layout.addLayout(dest_row)
        
        # Zona de Opciones (Stacked)
        self.dest_stack = QStackedWidget()
        
        # Pagina 0: Local
        local_page = QWidget()
        local_layout = QVBoxLayout(local_page)
        local_layout.setContentsMargins(0,0,0,0)
        local_lbl = QLabel("ℹ️ Se te solicitará la ubicación al iniciar la descarga.")
        local_lbl.setStyleSheet("color: #95a5a6; font-style: italic;")
        local_layout.addWidget(local_lbl)
        self.dest_stack.addWidget(local_page)
        
        # Pagina 1: Vultr S3
        vultr_page = QWidget()
        vultr_layout = QVBoxLayout(vultr_page)
        vultr_layout.setContentsMargins(0,0,0,0)
        
        bucket_row = QHBoxLayout()
        bucket_row.addWidget(QLabel("Bucket:"))
        self.bucket_combo = QComboBox()
        bucket_row.addWidget(self.bucket_combo)
        
        refresh_buckets = QPushButton("🔄")
        refresh_buckets.setToolTip("Recargar Buckets")
        refresh_buckets.setFixedWidth(30)
        refresh_buckets.clicked.connect(self.load_vultr_buckets)
        bucket_row.addWidget(refresh_buckets)
        vultr_layout.addLayout(bucket_row)
        
        self.delete_local_chk = QCheckBox("🗑️ Borrar archivo local tras subir")
        self.delete_local_chk.setChecked(True)
        vultr_layout.addWidget(self.delete_local_chk)
        
        self.dest_stack.addWidget(vultr_page)
        
        # Pagina 2: Azure Transfer
        azure_page = QWidget()
        azure_layout = QVBoxLayout(azure_page)
        azure_layout.setContentsMargins(0,0,0,0)
        
        # Perfil Destino
        prof_row = QHBoxLayout()
        prof_row.addWidget(QLabel("Perfil Destino:"))
        self.target_profile_combo = QComboBox()
        self.target_profile_combo.currentIndexChanged.connect(self.on_target_profile_changed)
        prof_row.addWidget(self.target_profile_combo)
        
        refresh_profs = QPushButton("🔄")
        refresh_profs.setFixedWidth(30)
        refresh_profs.clicked.connect(self.load_target_profiles)
        prof_row.addWidget(refresh_profs)
        azure_layout.addLayout(prof_row)
        
        # Resource Group Destino
        rg_row = QHBoxLayout()
        rg_row.addWidget(QLabel("Resource Group:"))
        self.target_rg_combo = QComboBox()
        self.target_rg_combo.setEditable(True) # Permitir escribir uno nuevo o existente
        self.target_rg_combo.setPlaceholderText("Selecciona o escribe RG destino")
        rg_row.addWidget(self.target_rg_combo)
        
        refresh_rg = QPushButton("🔄")
        refresh_rg.setFixedWidth(30)
        refresh_rg.clicked.connect(self.load_target_rgs)
        refresh_rg.setToolTip("Cargar Resource Groups del perfil destino")
        rg_row.addWidget(refresh_rg)
        azure_layout.addLayout(rg_row)
        
        # Location (Opcional, por defecto usa la del source o RG)
        # Por simplicidad, usaremos la misma location que el disco original por ahora,
        # o la del RG si se crea. Azure requiere location para crear disco.
        # Vamos a añadir un input de location editable.
        loc_row = QHBoxLayout()
        loc_row.addWidget(QLabel("Región (Location):"))
        self.target_location = QLineEdit()
        self.target_location.setPlaceholderText("ej: eastus (Dejar vacío para usar origen)")
        loc_row.addWidget(self.target_location)
        azure_layout.addLayout(loc_row)
        
        self.dest_stack.addWidget(azure_page)

        # Pagina 3: GCP Transfer
        gcp_page = QWidget()
        gcp_layout = QVBoxLayout(gcp_page)
        gcp_layout.setContentsMargins(0,0,0,0)
        
        # Info de Auth
        self.gcp_status_label = QLabel("Detectando credenciales GCP...")
        self.gcp_status_label.setStyleSheet("color: #7f8c8d; font-style: italic;")
        gcp_layout.addWidget(self.gcp_status_label)
        
        # Bucket Selector
        gcp_bucket_row = QHBoxLayout()
        gcp_bucket_row.addWidget(QLabel("Bucket GCP:"))
        self.gcp_bucket_combo = QComboBox()
        gcp_bucket_row.addWidget(self.gcp_bucket_combo)
        
        refresh_gcp = QPushButton("🔄")
        refresh_gcp.setFixedWidth(30)
        refresh_gcp.clicked.connect(self.load_gcp_buckets)
        gcp_bucket_row.addWidget(refresh_gcp)
        
        create_gcp_btn = QPushButton("➕ Nuevo Bucket")
        create_gcp_btn.clicked.connect(self.create_gcp_bucket)
        gcp_bucket_row.addWidget(create_gcp_btn)
        
        gcp_layout.addLayout(gcp_bucket_row)
        
        self.dest_stack.addWidget(gcp_page)
        
        dest_layout.addWidget(self.dest_stack)

        dest_group.setLayout(dest_layout)
        layout.addWidget(dest_group)
        
        self.download_progress = QProgressBar()
        self.download_progress.setVisible(False)
        layout.addWidget(self.download_progress)
        
        self.download_status = QLabel("")
        self.download_status.setVisible(False)
        layout.addWidget(self.download_status)
        
        return widget
    
    def create_help_tab(self):
        """Pestaña de ayuda"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        help_content = QWidget()
        help_layout = QVBoxLayout(help_content)
        
        help_text = QTextEdit()
        help_text.setHtml("""
        <h2>🔐 Métodos de Autenticación</h2>
        
        <h3>⭐ Login Interactivo (Recomendado)</h3>
        <p>El método más fácil. Solo necesitas tu cuenta de Microsoft.</p>
        
        <h3>📱 Código de Dispositivo</h3>
        <p>Útil cuando el navegador no puede abrirse automáticamente.</p>
        
        <h3>💻 Azure CLI</h3>
        <p>Usa las credenciales si ya tienes Azure CLI instalado.</p>
        
        <h3>🔑 Service Principal</h3>
        <p>Método avanzado, ver pestaña "Ayuda &amp; Docs" para instrucciones.</p>
        
        <hr>
        
        <h2>⚠️ Requisito Importante: Rol de Azure</h2>
        <p>Para descargar discos, tu cuenta necesita el rol:</p>
        <p style="background-color: #ffeb3b; padding: 10px; font-weight: bold;">
        Data Operator for Managed Disks
        </p>
        
        <h3>Cómo asignar el rol:</h3>
        <ol>
        <li>Ve a <b>Subscriptions</b> en Azure Portal</li>
        <li>Selecciona tu suscripción</li>
        <li>Click en <b>Access control (IAM)</b></li>
        <li>Click en <b>+ Add</b> → <b>Add role assignment</b></li>
        <li>Busca "Data Operator for Managed Disks"</li>
        <li>Asígnalo a tu usuario o Service Principal</li>
        </ol>
        """)
        help_text.setReadOnly(True)
        help_layout.addWidget(help_text)
        
        # Enlaces rápidos
        links_group = QGroupBox("🔗 Enlaces Rápidos")
        links_layout = QVBoxLayout()
        
        for text, url in [
            ("Portal de Azure", "https://portal.azure.com"),
            ("Subscriptions", "https://portal.azure.com/#view/Microsoft_Azure_Billing/SubscriptionsBlade"),
            ("App Registrations", "https://portal.azure.com/#view/Microsoft_AAD_IAM/ActiveDirectoryMenuBlade/~/RegisteredApps"),
            ("Instalar Azure CLI", "https://aka.ms/installazurecli"),
        ]:
            btn = QPushButton(f"🔗 {text}")
            btn.clicked.connect(lambda _, u=url: QDesktopServices.openUrl(QUrl(u)))
            btn.setStyleSheet("text-align: left; padding: 8px;")
            links_layout.addWidget(btn)
        
        links_group.setLayout(links_layout)
        help_layout.addWidget(links_group)
        
        scroll.setWidget(help_content)
        layout.addWidget(scroll)
        
        return widget
    
    # =========================================================================
    # MÉTODOS DE AUTENTICACIÓN
    # =========================================================================
    
    def get_subscription_id(self):
        sub_id = self.subscription_input.text().strip()
        if not sub_id:
            QMessageBox.warning(self, "Falta Subscription ID",
                "Por favor ingresa tu Subscription ID en la parte superior.")
            return None
        return sub_id
    
    def do_interactive_login(self):
        sub_id = self.get_subscription_id()
        if not sub_id:
            return
        
        self.interactive_btn.setEnabled(False)
        self.interactive_status.setText("🔄 Abriendo navegador...")
        self.interactive_status.setStyleSheet("color: #f39c12;")
        
        self.interactive_worker = InteractiveLoginWorker(sub_id)
        self.interactive_worker.finished.connect(self.on_interactive_finished)
        self.interactive_worker.start()
    
    def on_interactive_finished(self, success, message, credential):
        self.interactive_btn.setEnabled(True)
        self.interactive_status.setText(message)
        
        if success:
            self.interactive_status.setStyleSheet("color: #27ae60;")
            self.set_active_credential(credential, self.subscription_input.text().strip(), "interactive")
        else:
            self.interactive_status.setStyleSheet("color: #e74c3c;")
    
    def do_device_code_login(self):
        sub_id = self.get_subscription_id()
        if not sub_id:
            return
        
        self.device_code_btn.setEnabled(False)
        self.device_code_status.setText("🔄 Obteniendo código...")
        self.current_device_code = None
        
        self.device_code_worker = DeviceCodeLoginWorker(sub_id)
        self.device_code_worker.code_received.connect(self.on_device_code_received)
        self.device_code_worker.finished.connect(self.on_device_code_finished)
        self.device_code_worker.start()
    
    def on_device_code_received(self, user_code, verification_uri):
        self.current_device_code = user_code
        self.device_code_label.setText(
            f"<b style='font-size: 24px;'>{user_code}</b><br><br>"
            f"Ve a: <a href='{verification_uri}'>{verification_uri}</a><br>"
            "e ingresa este código"
        )
        self.device_code_copy_btn.setVisible(True)
        QDesktopServices.openUrl(QUrl(verification_uri))
    
    def copy_device_code(self):
        if self.current_device_code:
            QApplication.clipboard().setText(self.current_device_code)
            QMessageBox.information(self, "Copiado", "Código copiado al portapapeles")
    
    def on_device_code_finished(self, success, message, credential):
        self.device_code_btn.setEnabled(True)
        self.device_code_status.setText(message)
        
        if success:
            self.device_code_status.setStyleSheet("color: #27ae60;")
            self.set_active_credential(credential, self.subscription_input.text().strip(), "device_code")
        else:
            self.device_code_status.setStyleSheet("color: #e74c3c;")
    
    def do_cli_login(self):
        sub_id = self.get_subscription_id()
        if not sub_id:
            return
        
        self.cli_btn.setEnabled(False)
        self.cli_status.setText("🔄 Verificando Azure CLI...")
        
        self.cli_worker = AzureCliLoginWorker(sub_id)
        self.cli_worker.finished.connect(self.on_cli_finished)
        self.cli_worker.start()
    
    def on_cli_finished(self, success, message, credential):
        self.cli_btn.setEnabled(True)
        self.cli_status.setText(message)
        
        if success:
            self.cli_status.setStyleSheet("color: #27ae60;")
            self.set_active_credential(credential, self.subscription_input.text().strip(), "cli")
        else:
            self.cli_status.setStyleSheet("color: #e74c3c;")
    
    def do_service_principal_login(self):
        sub_id = self.get_subscription_id()
        if not sub_id:
            return
        
        tenant = self.sp_tenant_input.text().strip()
        client_id = self.sp_client_id_input.text().strip()
        secret = self.sp_client_secret_input.text().strip()
        
        if not all([tenant, client_id, secret]):
            QMessageBox.warning(self, "Campos incompletos",
                "Por favor completa todos los campos del Service Principal.")
            return
        
        self.sp_connect_btn.setEnabled(False)
        self.sp_status.setText("🔄 Conectando...")
        
        self.sp_worker = ServicePrincipalLoginWorker(tenant, client_id, secret, sub_id)
        self.sp_worker.finished.connect(self.on_sp_finished)
        self.sp_worker.start()
    
    def on_sp_finished(self, success, message, credential):
        self.sp_connect_btn.setEnabled(True)
        self.sp_status.setText(message)
        
        if success:
            self.sp_status.setStyleSheet("color: #27ae60;")
            self.set_active_credential(credential, self.subscription_input.text().strip(), "service_principal")
        else:
            self.sp_status.setStyleSheet("color: #e74c3c;")
    
    def set_active_credential(self, credential, subscription_id, method):
        """Establece la credencial activa para usar en operaciones"""
        self.active_credential = credential
        self.subscription_id = subscription_id
        self.auth_method = method
        
        method_names = {
            "interactive": "Cuenta Microsoft",
            "device_code": "Código de Dispositivo",
            "cli": "Azure CLI",
            "service_principal": "Service Principal"
        }
        
        self.connection_status.setText(f"✅ Conectado via {method_names.get(method, method)}")
        self.connection_status.setStyleSheet("font-size: 12px; color: #27ae60; padding: 5px; font-weight: bold;")
        
        # Guardar subscription para futuro uso
        self.save_subscription()
        
        QMessageBox.information(self, "Conectado",
            f"✅ Conexión exitosa!\n\nAhora puedes ir a la pestaña 'Mis Discos' para ver y descargar tus discos.")
    
    # =========================================================================
    # OPERACIONES DE DISCOS
    # =========================================================================
    
    def refresh_disks(self):
        if not self.active_credential:
            QMessageBox.warning(self, "No conectado",
                "Primero debes conectarte en la pestaña 'Autenticación'.")
            return
        
        self.disks_table.setRowCount(0)
        
        self.list_worker = ListDisksWorker(self.active_credential, self.subscription_id)
        self.list_worker.finished.connect(self.on_disks_listed)
        self.list_worker.start()
    
    def on_disks_listed(self, success, disks, message):
        if not success:
            QMessageBox.critical(self, "Error", message)
            return
        
        # Si la lista está vacía pero fue éxito (debug info)
        if not disks:
             QMessageBox.warning(self, "Información de Depuración", message)

        
        self.current_disks = disks
        self.disks_table.setRowCount(len(disks))
        
        for row, disk in enumerate(disks):
            self.disks_table.setItem(row, 0, QTableWidgetItem(disk['name']))
            self.disks_table.setItem(row, 1, QTableWidgetItem(disk['location']))
            self.disks_table.setItem(row, 2, QTableWidgetItem(str(disk['size_gb'])))
            self.disks_table.setItem(row, 3, QTableWidgetItem(disk['state']))
            self.disks_table.setItem(row, 4, QTableWidgetItem(disk['resource_group']))
            
            dl_btn = QPushButton("⬇️ Descargar")
            dl_btn.setStyleSheet("background-color: #3498db; color: white;")
            dl_btn.clicked.connect(lambda _, d=disk: self.download_disk(d))
            self.disks_table.setCellWidget(row, 5, dl_btn)

    def on_destination_changed(self, index):
        self.dest_stack.setCurrentIndex(index)
        if index == 1: # Vultr
            self.load_vultr_buckets()
        elif index == 2: # Azure
            self.load_target_profiles()
        elif index == 3: # GCP
            self.load_gcp_buckets()

    def _get_gcp_client(self):
        """Intenta obtener cliente GCP usando credenciales de carpeta Claves GCP"""
        try:
            from google.cloud import storage
            import glob
            
            # Si ya tenemos credenciales en ambiente
            if os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"):
                try:
                    client = storage.Client()
                    return client, None
                except:
                    pass
            
            # Buscar llave
            keys_dir = os.path.join(os.getcwd(), "Claves GCP")
            if not os.path.exists(keys_dir):
                return None, "Carpeta 'Claves GCP' no existe"
                
            json_files = glob.glob(os.path.join(keys_dir, "*.json"))
            if not json_files:
                return None, "No se encontraron .json en Claves GCP"
                
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = json_files[0]
            client = storage.Client()
            return client, None
        except Exception as e:
            return None, str(e)

    def load_gcp_buckets(self):
        client, error = self._get_gcp_client()
        if not client:
            self.gcp_status_label.setText(f"❌ Error GCP: {error}")
            self.gcp_bucket_combo.clear()
            QMessageBox.warning(self, "Error GCP", f"No se pudo conectar a GCP:\n{error}")
            return
            
        try:
            self.gcp_status_label.setText(f"✅ GCP Conectado: {client.project}")
            self.gcp_bucket_combo.clear()
            
            # Usar worker para listar (evitar freeze)
            self.gcp_list_worker = GCPWorker(lambda: [b.name for b in client.list_buckets()])
            self.gcp_list_worker.finished.connect(self.on_gcp_buckets_loaded)
            self.gcp_list_worker.start()
            
        except Exception as e:
             self.gcp_status_label.setText(f"❌ Error: {str(e)}")

    def on_gcp_buckets_loaded(self, success, buckets, message):
        if success:
            self.gcp_bucket_combo.addItems(buckets)
        else:
            QMessageBox.warning(self, "Error Listando Buckets", message)

    def create_gcp_bucket(self):
        client, error = self._get_gcp_client()
        if not client:
            QMessageBox.warning(self, "Error", f"No conectado a GCP: {error}")
            return
            
        name, ok = QInputDialog.getText(self, "Nuevo Bucket GCP", "Nombre del bucket (único globalmente):")
        if ok and name:
            # Sanitize bucket name to comply with GCP naming rules
            sanitized_name = self._sanitize_bucket_name(name)
            
            # Show user the sanitized name
            if sanitized_name != name:
                reply = QMessageBox.question(self, "Nombre Ajustado",
                    f"El nombre '{name}' fue ajustado a:\n'{sanitized_name}'\n\n(GCP solo permite minúsculas, números, guiones)\n\n¿Continuar?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                if reply != QMessageBox.StandardButton.Yes:
                    return
            
            try:
                bucket = client.create_bucket(sanitized_name, location="us")
                QMessageBox.information(self, "Éxito", f"Bucket GCP '{sanitized_name}' creado.")
                self.load_gcp_buckets()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error creando bucket GCP: {e}")
    
    def _sanitize_bucket_name(self, name: str) -> str:
        """
        Sanitize bucket name to comply with GCP naming rules:
        - 3-63 characters
        - Only lowercase letters, numbers, hyphens
        - Must start/end with letter or number
        - No underscores, spaces, or special characters
        """
        import unicodedata
        import re
        
        # Normalize unicode (remove accents)
        name = unicodedata.normalize('NFKD', name)
        name = name.encode('ASCII', 'ignore').decode('ASCII')
        
        # Convert to lowercase
        name = name.lower()
        
        # Replace spaces and underscores with hyphens
        name = name.replace(' ', '-').replace('_', '-')
        
        # Remove any character that's not lowercase, number, or hyphen
        name = re.sub(r'[^a-z0-9-]', '', name)
        
        # Remove consecutive hyphens
        name = re.sub(r'-+', '-', name)
        
        # Remove leading/trailing hyphens
        name = name.strip('-')
        
        # Ensure 3-63 characters
        if len(name) < 3:
            name = name + '-bucket'
        if len(name) > 63:
            name = name[:63].rstrip('-')
        
        return name


    def load_vultr_buckets(self):
        if not S3_AVAILABLE:
            QMessageBox.warning(self, "Error", "Módulo S3 no disponible")
            return
            
        # Get active Vultr profile
        cm = ConfigManager()
        vultr_profile = cm.get_active_profile()
        if not vultr_profile:
             # Try to find any profile if active is not set
             profiles = cm.list_profiles()
             if profiles:
                 vultr_profile = profiles[0]
             else:
                 QMessageBox.warning(self, "Aviso", "No hay perfiles de Vultr configurados. Ve a la pestaña de Vultr.")
                 return

        data = cm.get_config(vultr_profile)
        if not data:
            return

        try:
            s3 = S3Handler(data['access_key'], data['secret_key'], data['host_base'])
            buckets, error = s3.list_buckets()
            self.bucket_combo.clear()
            if buckets:
                self.bucket_combo.addItems(buckets)
            else:
                if error:
                     QMessageBox.warning(self, "Error S3", error)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error conectando a Vultr S3: {e}")

    def load_target_profiles(self):
        self.target_profile_combo.blockSignals(True)
        self.target_profile_combo.clear()
        current = self.current_profile_name
        for p_name in self.profiles.keys():
            if p_name != current:
                self.target_profile_combo.addItem(p_name)
        self.target_profile_combo.blockSignals(False)
        # Cargar RGs si hay perfil seleccionado
        if self.target_profile_combo.count() > 0:
            self.load_target_rgs()

    def on_target_profile_changed(self):
        self.load_target_rgs()

    def load_target_rgs(self):
        target_profile_name = self.target_profile_combo.currentText()
        if not target_profile_name:
            return
            
        profile = self.profiles.get(target_profile_name)
        if not profile: return
        
        # Necesitamos credenciales para este perfil
        # Para simplificar, usaremos la lógica de login 'silenciosa' o pediremos re-autenticación?
        # Reutilicemos la lógica que ya tenemos pero sin cambiar la UI principal.
        # Crearemos una credencial al vuelo.
        
        try:
            credential = self._create_credential_from_profile(profile)
            if not credential:
                self.target_rg_combo.clear()
                self.target_rg_combo.setPlaceholderText("No se pudo autenticar perfil destino")
                return

            self.target_rg_combo.setPlaceholderText("Cargando RGs...")
            self.rg_worker = GetResourceGroupsWorker(credential, profile.get('subscription_id'))
            self.rg_worker.finished.connect(self.on_target_rgs_loaded)
            self.rg_worker.start()
            
        except Exception as e:
            print(f"Error preparando credenciales destino: {e}")

    def on_target_rgs_loaded(self, rgs, error):
        self.target_rg_combo.clear()
        if error:
            self.target_rg_combo.setPlaceholderText("Error cargando RGs")
            QMessageBox.warning(self, "Error", f"No se pudieron cargar grupos de recursos:\n{error}")
        else:
            self.target_rg_combo.addItems(rgs)
            self.target_rg_combo.setPlaceholderText("Selecciona o escribe RG destino")

    def _create_credential_from_profile(self, profile):
        """Crea objeto credential basado en datos del perfil (sin UI)"""
        if not profile: return None
        
        from azure.identity import ClientSecretCredential, AzureCliCredential, InteractiveBrowserCredential
        
        method = profile.get('auth_method')
        
        if method == 'service_principal':
            return ClientSecretCredential(
                tenant_id=profile.get('tenant_id'),
                client_id=profile.get('client_id'),
                client_secret=profile.get('client_secret')
            )
        elif method == 'cli':
            return AzureCliCredential()
        # Para interactive/device, no podemos hacerlo background facilmente sin token cache (que no hemos implementado full)
        # Por ahora retornaremos None o Interactive (que abrirá browser si es necesario)
        # Intentemos InteractiveBrowserCredential pero podría bloquear si pide login
        return InteractiveBrowserCredential() 

    def download_disk(self, disk):
        if not self.active_credential:
            return
        
        # Check destination
        dest_index = self.dest_combo.currentIndex()
        
        file_path = ""
        is_temp = False
        
        if dest_index == 0: # Local
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Guardar disco como...",
                f"{disk['name']}.vhd",
                "VHD Files (*.vhd);;All Files (*)"
            )
            if not file_path:
                return
                
        elif dest_index == 1: # Vultr S3
            bucket = self.bucket_combo.currentText()
            if not bucket:
                QMessageBox.warning(self, "Error", "Selecciona un bucket de Vultr")
                return
            
            # Use temp folder
            import tempfile
            temp_dir = tempfile.gettempdir()
            file_path = os.path.join(temp_dir, f"{disk['name']}.vhd")
            is_temp = True
            
            reply = QMessageBox.question(self, "Confirmar Descarga y Subida", 
                f"El disco se descargará temporalmente a:\n{file_path}\n\nY luego se subirá al bucket:\n{bucket}\n\n¿Continuar?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply != QMessageBox.StandardButton.Yes:
                return

        elif dest_index == 2: # Azure Transfer
            tgt_profile_name = self.target_profile_combo.currentText()
            tgt_rg = self.target_rg_combo.currentText()
            
            if not tgt_profile_name or not tgt_rg:
                 QMessageBox.warning(self, "Error", "Selecciona un perfil y Resource Group de destino")
                 return
            
            tgt_profile = self.profiles.get(tgt_profile_name)
            tgt_loc = self.target_location.text().strip()
            if not tgt_loc:
                tgt_loc = disk['location'] # Usar la misma región que el original por defecto
            
            reply = QMessageBox.question(self, "Confirmar Transferencia", 
                f"TRANSFERENCIA DIRECTA NUBA-A-Nube\n\n"
                f"Origen: {disk['name']} ({disk['location']})\n"
                f"Destino: Perfil '{tgt_profile_name}' -> RG '{tgt_rg}' ({tgt_loc})\n\n"
                f"¿Iniciar transferencia?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            
            if reply != QMessageBox.StandardButton.Yes:
                return

            # Iniciar Transferencia
            self.download_progress.setVisible(True)
            self.download_progress.setValue(0)
            self.download_status.setVisible(True)
            self.download_status.setText("Iniciando transferencia...")
            
            tgt_cred = self._create_credential_from_profile(tgt_profile)
            
            self.transfer_worker = AzureTransferWorker(
                source_credential=self.active_credential,
                source_sub=self.subscription_id,
                source_rg=disk['resource_group'],
                disk_name=disk['name'],
                target_credential=tgt_cred,
                target_sub=tgt_profile.get('subscription_id'),
                target_rg=tgt_rg,
                target_location=tgt_loc
            )
            self.transfer_worker.progress.connect(self.on_download_progress)
            self.transfer_worker.finished.connect(self.on_transfer_finished)
            self.transfer_worker.start()
            return # Salir, no seguir con flujo de descarga local

        elif dest_index == 3: # GCP Transfer
            gcp_bucket = self.gcp_bucket_combo.currentText()
            if not gcp_bucket:
                QMessageBox.warning(self, "Error", "Selecciona un Bucket de GCP")
                return
            
            reply = QMessageBox.question(self, "Confirmar Transferencia GCP", 
                f"TRANSFERENCIA DIRECTA AZURE -> GCP\n\n"
                f"Origen: {disk['name']} ({disk['size_gb']} GB)\n"
                f"Destino: Bucket '{gcp_bucket}'\n"
                f"Modo: Streaming Directo (Sin descarga local)\n\n"
                f"¿Iniciar transferencia?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            
            if reply != QMessageBox.StandardButton.Yes:
                return
            
            self.download_progress.setVisible(True)
            self.download_progress.setValue(0)
            self.download_status.setVisible(True)
            self.download_status.setText("Iniciando streaming a GCP...")
            
            self.gcp_transfer_worker = AzureToGCPTransferWorker(
                azure_credential=self.active_credential,
                subscription_id=self.subscription_id,
                resource_group=disk['resource_group'],
                disk_name=disk['name'],
                gcp_bucket_name=gcp_bucket
            )
            self.gcp_transfer_worker.progress.connect(self.on_download_progress)
            self.gcp_transfer_worker.finished.connect(self.on_transfer_finished)
            self.gcp_transfer_worker.start()
            return

        self.download_progress.setVisible(True)
        self.download_progress.setValue(0)
        self.download_status.setVisible(True)
        
        self.download_worker = DownloadDiskWorker(
            self.active_credential,
            self.subscription_id,
            disk['resource_group'],
            disk['name'],
            file_path
        )
        self.download_worker.finished.connect(lambda s, m: self.on_download_finished_chain(s, m, dest_index, file_path, is_temp))
        self.download_worker.progress.connect(self.on_download_progress)
        self.download_worker.start()

    def on_transfer_finished(self, success, message):
        self.download_progress.setVisible(False)
        self.download_status.setVisible(False)
        if success:
            QMessageBox.information(self, "Transferencia Exitosa", message)
        else:
            QMessageBox.critical(self, "Error en Transferencia", message)

    def on_download_finished_chain(self, success, message, dest_index, file_path, is_temp):
        if not success:
            self.on_download_finished(False, message)
            return
            
        if dest_index == 0 or dest_index == 2: # Local or Azure (fallback)
             self.on_download_finished(True, message)
        
        elif dest_index == 1: # Vultr S3
            self.download_status.setText("⬆️ Iniciando subida a Vultr S3...")
            bucket = self.bucket_combo.currentText()
            
            # Initialize S3 Handler
            cm = ConfigManager()
            vultr_profile = cm.get_active_profile()
            if not vultr_profile:
                # Fallback check
                profs = cm.list_profiles()
                if profs: vultr_profile = profs[0]

            data = cm.get_config(vultr_profile)
            if not data:
                self.on_download_finished(False, "No se pudieron cargar las credenciales de Vultr para la subida.")
                return
                
            s3 = S3Handler(data['access_key'], data['secret_key'], data['host_base'])
            
            self.upload_worker = S3UploadWorker(s3, bucket, file_path)
            self.upload_worker.progress.connect(self.on_download_progress) # Reuse progress bar
            self.upload_worker.finished.connect(lambda s, m: self.on_upload_finished(s, m, file_path, is_temp))
            self.upload_worker.start()
            
    def on_upload_finished(self, success, message, file_path, is_temp):
        self.download_progress.setVisible(False)
        self.download_status.setVisible(False)
        
        if success:
            QMessageBox.information(self, "Proceso Completado", message)
            if is_temp and self.delete_local_chk.isChecked():
                try:
                    os.remove(file_path)
                    print(f"Archivo temporal eliminado: {file_path}")
                except Exception as e:
                    print(f"Error borrando temp: {e}")
        else:
             QMessageBox.critical(self, "Error en Subida", message)
    
    def on_download_progress(self, pct, msg):
        self.download_progress.setValue(pct)
        self.download_status.setText(msg)
    
    def on_download_finished(self, success, message):
        self.download_progress.setVisible(False)
        self.download_status.setVisible(False)
        
        if success:
            QMessageBox.information(self, "Éxito", message)
        else:
            QMessageBox.critical(self, "Error", message)
    
    # =========================================================================
    # PERSISTENCIA
    # =========================================================================
    
    def get_config_path(self):
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base, "azure_config.json")
    
    def save_subscription(self):
        try:
            config = {"subscription_id": self.subscription_id}
            with open(self.get_config_path(), 'w') as f:
                json.dump(config, f)
        except:
            pass
    
    def load_saved_subscription(self):
        try:
            with open(self.get_config_path(), 'r') as f:
                config = json.load(f)
                self.subscription_input.setText(config.get('subscription_id', ''))
        except:
            pass
    
    
    # =========================================================================
    # GESTIÓN DE PERFILES
    # =========================================================================
    
    def get_profiles_path(self):
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base, "azure_profiles.json")
    
    def load_profiles(self):
        """Carga los perfiles desde JSON"""
        self.profile_combo.blockSignals(True)
        self.profile_combo.clear()
        self.profiles = {}
        
        path = self.get_profiles_path()
        active_profile = None
        
        if os.path.exists(path):
            try:
                with open(path, 'r') as f:
                    data = json.load(f)
                    for p in data.get('profiles', []):
                        self.profiles[p['name']] = p
                    active_profile = data.get('active_profile')
            except Exception as e:
                print(f"Error loading profiles: {e}")
        
        if not self.profiles:
            # Crear perfil por defecto si no existe
            self.profiles["Default"] = {"name": "Default"}
        
        self.profile_combo.addItems(list(self.profiles.keys()))
        
        if active_profile and active_profile in self.profiles:
            self.profile_combo.setCurrentText(active_profile)
            self.load_profile_data(active_profile)
        else:
            self.profile_combo.setCurrentIndex(0)
            self.load_profile_data(self.profile_combo.currentText())
            
        self.profile_combo.blockSignals(False)

    def save_profiles(self):
        """Guarda los perfiles en JSON"""
        data = {
            "active_profile": self.current_profile_name,
            "profiles": list(self.profiles.values())
        }
        try:
            with open(self.get_profiles_path(), 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al guardar perfiles: {e}")

    def on_profile_changed(self, index):
        """Cambia el perfil activo"""
        name = self.profile_combo.currentText()
        self.load_profile_data(name)
        self.save_profiles() # Save active profile change

    def load_profile_data(self, profile_name):
        """Carga los datos del perfil en los campos"""
        self.current_profile_name = profile_name
        profile = self.profiles.get(profile_name, {})
        
        # Cargar Subscription ID
        self.subscription_input.setText(profile.get('subscription_id', ''))
        
        # Cargar Credenciales SP si existen
        self.sp_tenant_input.setText(profile.get('tenant_id', ''))
        self.sp_client_id_input.setText(profile.get('client_id', ''))
        self.sp_client_secret_input.setText(profile.get('client_secret', ''))
        
        # Si tiene auth_method service_principal, seleccionar esa pestaña
        if profile.get('auth_method') == 'service_principal':
            self.auth_tabs.setCurrentIndex(3) # Service Principal tab
        
        self.connection_status.setText(f"👤 Perfil activo: {profile_name}")
        self.active_credential = None # Reset credential on profile switch

    def update_current_profile_data(self):
        """Actualiza los datos del perfil actual con lo que hay en los inputs"""
        if not self.current_profile_name:
            return
            
        profile = self.profiles[self.current_profile_name]
        profile['subscription_id'] = self.subscription_input.text().strip()
        profile['tenant_id'] = self.sp_tenant_input.text().strip()
        profile['client_id'] = self.sp_client_id_input.text().strip()
        profile['client_secret'] = self.sp_client_secret_input.text().strip()
        
        # Guardar automáticamente
        self.save_profiles()

    def create_new_profile(self):
        """Crea un nuevo perfil"""
        name, ok = QInputDialog.getText(self, "Nuevo Perfil", "Nombre del Perfil:")
        if ok and name:
            if name in self.profiles:
                QMessageBox.warning(self, "Error", "El nombre de perfil ya existe.")
                return
            
            self.profiles[name] = {"name": name}
            self.profile_combo.addItem(name)
            self.profile_combo.setCurrentText(name)
            self.save_profiles()

    def delete_current_profile(self):
        """Borra el perfil actual"""
        name = self.profile_combo.currentText()
        if len(self.profiles) <= 1:
            QMessageBox.warning(self, "Error", "No puedes borrar el último perfil.")
            return
            
        confirm = QMessageBox.question(self, "Confirmar", 
                                     f"¿Estás seguro de borrar el perfil '{name}'?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if confirm == QMessageBox.StandardButton.Yes:
            del self.profiles[name]
            self.load_profiles()
            self.save_profiles()

    # Sobreescribir métodos de guardado antiguos para usar el sistema de perfiles
    def save_subscription(self):
        self.update_current_profile_data()
    
    def load_saved_subscription(self):
        pass # Ya se maneja en load_profiles
    
    def save_sp_credentials(self):
        self.update_current_profile_data()
        QMessageBox.information(self, "Guardado", f"Credenciales guardadas en perfil '{self.current_profile_name}'")
    
    def load_sp_credentials(self):
        pass # Ya se maneja en load_profiles
    
    # =================================================================
    # TRANSFER QUEUE - Resume Handler
    # =================================================================
    
    def on_resume_transfer(self, transfer_id: str):
        """Reanudar una transferencia pausada desde el TransferQueueWidget"""
        if not TRANSFER_MANAGER_AVAILABLE or not self.transfer_manager:
            return
            
        transfer = self.transfer_manager.get_transfer(transfer_id)
        if not transfer:
            QMessageBox.warning(self, "Error", "Transferencia no encontrada")
            return
        
        # Check if SAS URL is still valid
        if not transfer.sas_url:
            # Need to get a new SAS - requires fresh credentials
            if not self.active_credential:
                QMessageBox.warning(self, "Error", 
                    "Debes conectarte primero para obtener un nuevo SAS URL.\n"
                    "Después podrás reanudar la descarga.")
                return
            
            # Will get new SAS in worker
            sas_url = None
        else:
            # Use existing SAS URL
            sas_url = transfer.sas_url
        
        # Create worker for resume
        worker = DownloadDiskWorker(
            credential=self.active_credential,
            subscription_id=transfer.subscription_id,
            resource_group=transfer.resource_group,
            disk_name=transfer.disk_name,
            output_path=transfer.destination,
            sas_url=sas_url,
            start_byte=transfer.bytes_transferred,
            transfer_id=transfer_id
        )
        
        # Connect signals to TransferManager
        def update_transfer_progress(bytes_dl, total_bytes):
            self.transfer_manager.update_progress(
                transfer_id, bytes_dl, 
                f"Descargando: {bytes_dl/(1024**3):.2f} / {total_bytes/(1024**3):.2f} GB",
                total_bytes
            )
        
        def on_worker_finished(success, message):
            self.transfer_manager.complete_transfer(transfer_id, success, message)
        
        worker.progress_bytes.connect(update_transfer_progress)
        worker.finished.connect(on_worker_finished)
        
        # Register worker with manager
        self.transfer_manager.register_worker(transfer_id, worker)
        
        # Update status
        transfer.status = TransferStatus.RUNNING.value
        
        worker.start()
        QMessageBox.information(self, "Reanudando", 
            f"Reanudando descarga de:\n{transfer.name}\n\nDesde: {transfer.bytes_transferred/(1024**3):.2f} GB")
