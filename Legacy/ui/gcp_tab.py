"""
Google Cloud Platform Tab - Gestión de Storage
Permite autenticarse con Service Account y gestionar Buckets/Objetos.
"""

import os
import glob
import shutil
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGroupBox, QListWidget, QListWidgetItem, QFileDialog, 
    QMessageBox, QProgressBar, QSplitter, QFrame, QScrollArea,
    QMenu, QInputDialog, QTreeWidget, QTreeWidgetItem, QTabWidget
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSize, QTimer
from PyQt6.QtGui import QIcon, QAction
from google.cloud import storage
from datetime import datetime
from transfer_manager import get_transfer_manager, TransferType, TransferStatus
import re
from ui.transfer_queue_widget import TransferQueueWidget
from ui.gcp_sync_tab import GCPSyncTab

class GCPWorker(QThread):
    """Worker genérico para operaciones de GCP que pueden bloquear la UI"""
    finished = pyqtSignal(bool, object, str)
    
    def __init__(self, func, *args, **kwargs):
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs
        
    def run(self):
        try:
            result = self.func(*self.args, **self.kwargs)
            self.finished.emit(True, result, "Operación exitosa")
        except Exception as e:
            self.finished.emit(False, None, str(e))

class GCPFolderUploadWorker(QThread):
    finished = pyqtSignal(bool, str)
    progress = pyqtSignal(str)

    def __init__(self, bucket, local_folder):
        super().__init__()
        self.bucket = bucket
        self.local_folder = local_folder
        self._is_running = True

    def run(self):
        try:
            folder_name = os.path.basename(self.local_folder)
            uploaded_count = 0
            
            for root, dirs, files in os.walk(self.local_folder):
                if not self._is_running: break
                for file in files:
                    if not self._is_running: break
                    local_path = os.path.join(root, file)
                    rel_path = os.path.relpath(local_path, self.local_folder)
                    blob_name = f"{folder_name}/{rel_path}".replace("\\", "/") # Normalize separators
                    
                    self.progress.emit(f"Subiendo {blob_name}...")
                    blob = self.bucket.blob(blob_name)
                    blob.upload_from_filename(local_path)
                    uploaded_count += 1
            
            if self._is_running:
                self.finished.emit(True, f"Se subieron {uploaded_count} archivos correctamente.")
            else:
                self.finished.emit(False, "Operación cancelada.")
                
        except Exception as e:
            self.finished.emit(False, str(e))

    def stop(self):
        self._is_running = False


class GCPDownloadWorker(QThread):
    """Worker para descargas desde GCP integrado con TransferManager"""
    finished = pyqtSignal(bool, str)
    
    def __init__(self, blob, save_path, transfer_id):
        super().__init__()
        self.blob = blob
        self.save_path = save_path
        self.transfer_id = transfer_id
        self.transfer_manager = get_transfer_manager()
        self._is_running = True
        
    def run(self):
        import time
        try:
            total_size = self.blob.size or 0
            
            # Verificar si existe el transfer antes de iniciar
            info = self.transfer_manager.get_transfer(self.transfer_id)
            if not info:
                self.finished.emit(False, "Transferencia no encontrada")
                return

            self.transfer_manager.update_progress(self.transfer_id, 0, "Iniciando...", total_size)
            
            downloaded = 0
            # Chunk size 1MB
            chunk_size = 1024 * 1024 
            
            # Usar blob.open('rb') para streaming eficiente
            with open(self.save_path, 'wb') as f:
                with self.blob.open('rb') as stream:
                    while True:
                        if not self._is_running:
                            self.transfer_manager.update_transfer(self.transfer_id, status=TransferStatus.CANCELLED)
                            self.finished.emit(False, "Descarga cancelada")
                            return
                            
                        # Verificar estado en el manager (Pausa/Cancelación desde UI)
                        info = self.transfer_manager.get_transfer(self.transfer_id)
                        if not info: break # Eliminado
                        
                        if info.status == TransferStatus.PAUSED:
                            time.sleep(0.5)
                            continue
                        elif info.status == TransferStatus.CANCELLED:
                            self._is_running = False
                            continue
                            
                        chunk = stream.read(chunk_size)
                        if not chunk:
                            break
                            
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        # Actualizar progreso
                        speed_val = 0 # Calculate speed if needed
                        self.transfer_manager.update_progress(
                            self.transfer_id, 
                            downloaded,
                            "",
                            total_size
                        )
            
            if self._is_running:
                self.transfer_manager.complete_transfer(self.transfer_id, True, "Descarga completada exitosamente")
                self.finished.emit(True, "Descarga completada exitosamente")
            
        except Exception as e:
            error_msg = str(e)
            if not error_msg: 
                error_msg = repr(e) # Capturar mensaje si str() está vacío
            
            self.transfer_manager.complete_transfer(self.transfer_id, False, error_msg)
            self.finished.emit(False, error_msg)
    
    def stop(self):
        self._is_running = False


class GCPTab(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.client = None
        self.current_bucket = None
        self.project_id = None
        self.active_workers = set()
        self.transfer_manager = get_transfer_manager()
        
        self.init_ui()
        # Auto-auth re-enabled with safe delay.
        self.try_auto_auth()

    def init_ui(self):
        # Layout principal
        if self.layout() is None:
            main_layout = QVBoxLayout(self)
            main_layout.setContentsMargins(0, 0, 0, 0)
            main_layout.setSpacing(0)
        else:
            main_layout = self.layout()
        
        # --- TAB WIDGET PRINCIPAL ---
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)
        
        # ==========================================
        # TAB 1: EXPLORADOR (Código original movido)
        # ==========================================
        self.explorer_tab = QWidget()
        explorer_layout = QVBoxLayout(self.explorer_tab)
        explorer_layout.setSpacing(10)
        explorer_layout.setContentsMargins(15, 15, 15, 15)
        
        # Header
        header = QLabel("☁️ Google Cloud Storage - Explorador")
        header.setStyleSheet("font-size: 18px; font-weight: bold; color: #4285F4;")
        explorer_layout.addWidget(header)
        
        # Estado de conexión
        self.connection_status = QLabel("⚪ Buscando credenciales...")
        self.connection_status.setStyleSheet("font-size: 12px; color: #7f8c8d; padding: 5px;")
        explorer_layout.addWidget(self.connection_status)

        # Cola de transferencias (reemplaza barra de progreso simple)
        self.transfer_queue = TransferQueueWidget()
        self.transfer_queue.setMaximumHeight(200) # Limitar altura
        explorer_layout.addWidget(self.transfer_queue)

        # Botón de conectar manual
        self.connect_btn = QPushButton("🔌 Conectar con GCP")
        self.connect_btn.clicked.connect(self.try_auto_auth)
        self.connect_btn.setStyleSheet("background-color: #2c3e50; color: white; padding: 5px;")
        explorer_layout.addWidget(self.connect_btn)

        # Botón para subir credenciales (New)
        self.upload_creds_btn = QPushButton("🔑 Subir Credenciales JSON")
        self.upload_creds_btn.clicked.connect(self.upload_credentials)
        self.upload_creds_btn.setStyleSheet("background-color: #e67e22; color: white; padding: 5px;")
        explorer_layout.addWidget(self.upload_creds_btn)
        
        # Splitter principal
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Panel Izquierdo: Buckets
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        buckets_group = QGroupBox("🗂️ Buckets")
        buckets_layout = QVBoxLayout()
        
        self.buckets_list = QListWidget()
        self.buckets_list.itemClicked.connect(self.on_bucket_selected)
        buckets_layout.addWidget(self.buckets_list)
        
        bucket_actions = QHBoxLayout()
        self.refresh_btn = QPushButton("🔄")
        self.refresh_btn.setFixedWidth(30)
        self.refresh_btn.clicked.connect(self.refresh_buckets)
        
        self.create_bucket_btn = QPushButton("➕ Nuevo Bucket")
        self.create_bucket_btn.clicked.connect(self.create_new_bucket)
        
        bucket_actions.addWidget(self.create_bucket_btn)
        bucket_actions.addWidget(self.refresh_btn)
        buckets_layout.addLayout(bucket_actions)
        
        buckets_group.setLayout(buckets_layout)
        left_layout.addWidget(buckets_group)
        
        splitter.addWidget(left_widget)
        
        # Panel Derecho: Objetos explorador
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        objects_group = QGroupBox("📄 Archivos y Carpetas")
        objects_layout = QVBoxLayout()
        
        self.objects_tree = QTreeWidget()
        self.objects_tree.setHeaderLabels(["Nombre", "Tamaño", "Modificado"])
        self.objects_tree.setColumnWidth(0, 300)
        # Habilitar selección múltiple si se desea, por ahora simple
        objects_layout.addWidget(self.objects_tree)
        
        obj_actions = QHBoxLayout()
        self.upload_file_btn = QPushButton("📄 Subir Archivo")
        self.upload_file_btn.clicked.connect(self.upload_file)
        self.upload_file_btn.setEnabled(False)
        
        self.upload_folder_btn = QPushButton("📁 Subir Carpeta")
        self.upload_folder_btn.clicked.connect(self.upload_folder)
        self.upload_folder_btn.setEnabled(False)
        
        self.download_btn = QPushButton("⬇️ Descargar")
        self.download_btn.clicked.connect(self.download_selected)
        self.download_btn.setEnabled(False)
        
        # Styling buttons
        for btn in [self.upload_file_btn, self.upload_folder_btn]:
            btn.setStyleSheet("background-color: #4285F4; color: white; font-weight: bold;")
            
        obj_actions.addWidget(self.upload_file_btn)
        obj_actions.addWidget(self.upload_folder_btn)
        obj_actions.addWidget(self.download_btn)
        objects_layout.addLayout(obj_actions)
        
        objects_group.setLayout(objects_layout)
        right_layout.addWidget(objects_group)
        
        splitter.addWidget(right_widget)
        splitter.setSizes([250, 550])
        
        explorer_layout.addWidget(splitter, 1)
        
        # Scroll area para el tab explorador (opcional, si se quiere scroll)
        # En este diseño removemos el scroll global para usar el del tree/list
        
        self.tabs.addTab(self.explorer_tab, "🔍 Explorador")

        # ==========================================
        # TAB 2: SINCRONIZACIÓN (Nuevo)
        # ==========================================
        self.sync_tab = GCPSyncTab(self.main_window)
        self.tabs.addTab(self.sync_tab, "🔄 Sincronización Automática")

    def try_auto_auth(self):
        """Intenta autenticarse automáticamente buscando JSON en 'Claves GCP'"""
        self.connection_status.setText("⏳ Conectando automáticamente en 2s...")
        self.connect_btn.setEnabled(False)
        self.upload_creds_btn.setEnabled(False)
        # Delay increased to 2000ms to ensure MainWindow is fully rendered and avoid startup race conditions
        QTimer.singleShot(2000, self._perform_auth_main_thread)

    def _perform_auth_main_thread(self):
        try:
            # Buscar archivo JSON en la carpeta Claves GCP
            keys_dir = os.path.join(os.getcwd(), "Claves GCP")
            if not os.path.exists(keys_dir):
                self.connection_status.setText("❌ Carpeta 'Claves GCP' no encontrada")
                self.connect_btn.setEnabled(True)
                self.upload_creds_btn.setEnabled(True)
                return

            json_files = glob.glob(os.path.join(keys_dir, "*.json"))
            if not json_files:
                self.connection_status.setText("❌ No se encontró archivo .json en 'Claves GCP'")
                self.connect_btn.setEnabled(True)
                self.upload_creds_btn.setEnabled(True)
                return

            # Usar el primer archivo encontrado
            key_path = json_files[0]
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = key_path
            
            self.client = storage.Client()
            self.project_id = self.client.project
            
            self.connection_status.setText(f"✅ Conectado | Proyecto: {self.project_id}")
            self.connect_btn.hide() # Ocultar botón si conecta bien
            self.upload_creds_btn.hide() # Ocultar botón de subida si conecta bien
            self.refresh_buckets()
            
            # Pasar cliente a la pestaña de sincronización
            if hasattr(self, 'sync_tab'):
                self.sync_tab.set_client(self.client)
            
        except Exception as e:
            self.connection_status.setText(f"❌ Error de conexión: {str(e)}")
            self.connect_btn.setEnabled(True)
            self.connect_btn.setText("Reintentar Conexión")
            self.upload_creds_btn.setEnabled(True)
            QMessageBox.critical(self, "Error GCP", f"No se pudo conectar a Google Cloud:\n{str(e)}")

    def upload_credentials(self):
        """Permite al usuario subir un archivo JSON de credenciales"""
        path, _ = QFileDialog.getOpenFileName(self, "Seleccionar Credenciales GCP", "", "JSON Files (*.json)")
        if path:
            try:
                # Crear carpeta si no existe
                keys_dir = os.path.join(os.getcwd(), "Claves GCP")
                if not os.path.exists(keys_dir):
                    os.makedirs(keys_dir)
                
                # Copiar archivo
                start_path = path
                filename = os.path.basename(path)
                dest_path = os.path.join(keys_dir, filename)
                
                # Limpiar otros json previos para evitar conflictos (opcional, pero recomendado)
                for old_file in glob.glob(os.path.join(keys_dir, "*.json")):
                    try:
                        os.remove(old_file)
                    except:
                        pass # Si no se puede borrar, seguimos

                shutil.copy2(start_path, dest_path)
                
                QMessageBox.information(self, "Credenciales", "Credenciales subidas correctamente. Conectando...")
                self.try_auto_auth()
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al subir credenciales: {str(e)}")

    def _handle_auth_error(self, message):
        self.connection_status.setText(f"❌ Error: {message}")
        self.connection_status.setStyleSheet("font-size: 12px; color: #c0392b; padding: 5px;")
        self.connect_btn.setEnabled(True)

    def _do_auth(self, key_path):
        # Deprecated: Auth now happens in main thread
        pass

    def on_auth_finished(self, success, result, message):
        # Deprecated
        pass

    def refresh_buckets(self):
        if not self.client: return
        self.refresh_btn.setEnabled(False)
        self.buckets_list.clear()
        
        # Use worker pool to track active threads and prevent GC
        worker = GCPWorker(lambda: list(self.client.list_buckets()))
        worker.finished.connect(self.on_buckets_loaded)
        # Connect cleanup slot
        worker.finished.connect(lambda: self.cleanup_worker(worker))
        
        self.active_workers.add(worker)
        worker.start()

    def cleanup_worker(self, worker):
        if worker in self.active_workers:
            self.active_workers.remove(worker)

    def on_buckets_loaded(self, success, buckets, message):
        self.refresh_btn.setEnabled(True)
        if success:
            self.buckets_list.clear()
            for bucket in buckets:
                item = QListWidgetItem(f"📦 {bucket.name}")
                item.setData(Qt.ItemDataRole.UserRole, bucket)
                self.buckets_list.addItem(item)
            
            # Sincronizar con la pestaña de Sync
            if hasattr(self, 'sync_tab'):
                self.sync_tab.update_buckets_from_list(buckets)
        else:
            QMessageBox.warning(self, "Error", f"No se pudieron cargar buckets: {message}")

    def create_new_bucket(self):
        if not self.client: return
        name, ok = QInputDialog.getText(self, "Nuevo Bucket", "Nombre del bucket (único globalmente):\n(Se formateará automáticamente)")
        if ok and name:
            # Auto-formato de nombre
            original_name = name
            # 1. Minúsculas
            name = name.lower()
            # 2. Reemplazar caracteres inválidos (espacios, símbolos) por guiones
            name = re.sub(r'[^a-z0-9-]', '-', name)
            # 3. Eliminar guiones múltiples
            name = re.sub(r'-+', '-', name)
            # 4. Eliminar guiones al inicio y final
            name = name.strip('-')
            
            if not name:
                QMessageBox.warning(self, "Nombre Inválido", "El nombre resultante quedó vacío.")
                return

            try:
                bucket = self.client.create_bucket(name, location="us")
                msg = f"Bucket creado exitosamente:\nOriginal: '{original_name}'\nFormateado: '{name}'"
                QMessageBox.information(self, "Éxito", msg)
                self.refresh_buckets()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al crear bucket '{name}':\n{str(e)}")

    def on_bucket_selected(self, item):
        bucket = item.data(Qt.ItemDataRole.UserRole)
        self.current_bucket = bucket
        self.upload_file_btn.setEnabled(True)
        self.upload_folder_btn.setEnabled(True)
        self.download_btn.setEnabled(True) # Activar descarga
        self.refresh_objects()

    def refresh_objects(self):
        if not self.current_bucket: return
        self.objects_tree.clear()
        
        worker = GCPWorker(lambda: list(self.client.list_blobs(self.current_bucket)))
        worker.finished.connect(self.on_objects_loaded)
        worker.finished.connect(lambda: self.cleanup_worker(worker))
        
        self.active_workers.add(worker)
        worker.start()

    def on_objects_loaded(self, success, blobs, message):
        if success:
            # Diccionario para mapear rutas a nodos del árbol
            folder_items = {}
            
            # Ordenar blobs: carpetas primero, luego por nombre
            sorted_blobs = sorted(blobs, key=lambda b: (not b.name.endswith('/'), b.name.lower()))
            
            for blob in sorted_blobs:
                size_str = f"{blob.size / 1024:.2f} KB" if blob.size else "0 KB"
                if blob.size and blob.size > 1024 * 1024:
                    size_str = f"{blob.size / (1024*1024):.2f} MB"
                updated = blob.updated.strftime("%Y-%m-%d %H:%M") if blob.updated else "-"
                
                # Separar la ruta en partes
                parts = blob.name.split('/')
                
                # Construir la jerarquía
                current_path = ""
                parent_item = None
                
                for i, part in enumerate(parts):
                    if not part:  # Ignorar partes vacías
                        continue
                        
                    if current_path:
                        current_path += "/" + part
                    else:
                        current_path = part
                    
                    is_last = (i == len(parts) - 1)
                    
                    if current_path in folder_items:
                        # Ya existe este nodo
                        parent_item = folder_items[current_path]
                    else:
                        # Crear nuevo nodo
                        if is_last and not blob.name.endswith('/'):
                            # Es un archivo (hoja) - determinar icono por extensión
                            icon = self._get_file_icon(part)
                            item = QTreeWidgetItem([f"{icon} {part}", size_str, updated])
                            item.setData(0, Qt.ItemDataRole.UserRole, blob)
                        else:
                            # Es una carpeta
                            item = QTreeWidgetItem(["📁 " + part, "", ""])
                            item.setData(0, Qt.ItemDataRole.UserRole, None)
                        
                        if parent_item:
                            parent_item.addChild(item)
                        else:
                            self.objects_tree.addTopLevelItem(item)
                        
                        folder_items[current_path] = item
                        parent_item = item
            
            # Expandir el primer nivel
            for i in range(self.objects_tree.topLevelItemCount()):
                self.objects_tree.topLevelItem(i).setExpanded(True)
                
            # Ajustar columnas
            self.objects_tree.resizeColumnToContents(0)
        else:
            QMessageBox.warning(self, "Error", f"No se pudieron listar objetos: {message}")

    def _get_file_icon(self, filename):
        """Devuelve un emoji de icono basado en la extensión del archivo"""
        ext = filename.lower().split('.')[-1] if '.' in filename else ''
        icons = {
            # Imágenes
            'jpg': '🖼️', 'jpeg': '🖼️', 'png': '🖼️', 'gif': '🖼️', 'bmp': '🖼️', 'webp': '🖼️', 'svg': '🖼️',
            # Videos
            'mp4': '🎬', 'avi': '🎬', 'mkv': '🎬', 'mov': '🎬', 'wmv': '🎬', 'flv': '🎬', 'webm': '🎬',
            # Audio
            'mp3': '🎵', 'wav': '🎵', 'flac': '🎵', 'aac': '🎵', 'ogg': '🎵', 'm4a': '🎵',
            # Documentos
            'pdf': '📕', 'doc': '📘', 'docx': '📘', 'xls': '📗', 'xlsx': '📗', 'ppt': '📙', 'pptx': '📙',
            'txt': '📄', 'md': '📄', 'rtf': '📄',
            # Código
            'py': '🐍', 'js': '📜', 'html': '🌐', 'css': '🎨', 'json': '📋', 'xml': '📋', 'yaml': '📋', 'yml': '📋',
            # Comprimidos
            'zip': '📦', 'rar': '📦', '7z': '📦', 'tar': '📦', 'gz': '📦', 'bz2': '📦',
            # Ejecutables
            'exe': '⚙️', 'msi': '⚙️', 'bat': '⚙️', 'sh': '⚙️', 'ps1': '⚙️',
            # Discos
            'iso': '💿', 'img': '💿', 'vhd': '💿', 'vhdx': '💿', 'vmdk': '💿',
            # Datos
            'sql': '🗃️', 'db': '🗃️', 'sqlite': '🗃️', 'csv': '📊',
        }
        return icons.get(ext, '📄')

    def upload_file(self):
        if not self.current_bucket: return
        path, _ = QFileDialog.getOpenFileName(self, "Seleccionar Archivo")
        if path:
            filename = os.path.basename(path)
            blob = self.current_bucket.blob(filename)
            
            # Usar worker para no congelar UI
            worker = GCPWorker(self._upload_thread, blob, path)
            worker.finished.connect(self.on_upload_finished)
            worker.finished.connect(lambda: self.cleanup_worker(worker))
            self.active_workers.add(worker)
            worker.start()
            self.connection_status.setText(f"⏳ Subiendo {filename}...")

    def _upload_thread(self, blob, path):
        blob.upload_from_filename(path)
        return True

    def on_upload_finished(self, success, result, message):
        if success:
            QMessageBox.information(self, "Éxito", "Archivo subido correctamente.")
            self.refresh_objects()
        else:
            QMessageBox.critical(self, "Error", f"Error al subir: {message}")
        self.connection_status.setText(f"✅ Conectado | Proyecto: {self.project_id}")

    def upload_folder(self):
        if not self.current_bucket: return
        folder_path = QFileDialog.getExistingDirectory(self, "Seleccionar Carpeta")
        if folder_path:
            folder_name = os.path.basename(folder_path)
            
            # Usar el worker recursivo
            worker = GCPFolderUploadWorker(self.current_bucket, folder_path)
            worker.progress.connect(lambda msg: self.connection_status.setText(f"⏳ {msg}"))
            worker.finished.connect(self.on_upload_folder_finished)
            worker.finished.connect(lambda: self.cleanup_worker(worker))
            
            self.active_workers.add(worker)
            worker.start()

    def on_upload_folder_finished(self, success, message):
        if success:
            QMessageBox.information(self, "Éxito", message)
            self.refresh_objects()
        else:
            QMessageBox.critical(self, "Error", f"Error al subir carpeta: {message}")
        
        self.connection_status.setText(f"✅ Conectado | Proyecto: {self.project_id}")

    def download_selected(self):
        item = self.objects_tree.currentItem()
        if not item:
            QMessageBox.warning(self, "Selección", "Por favor seleccione un archivo para descargar.")
            return
            
        blob = item.data(0, Qt.ItemDataRole.UserRole)
        if not blob:
            QMessageBox.information(self, "GCP", "Seleccione un archivo, no una carpeta.")
            return

        # Si el blob termina en '/' es pseudo-carpeta, no descargar
        if blob.name.endswith('/'):
             QMessageBox.information(self, "GCP", "La descarga de carpetas no está soportada directamente en esta versión.")
             return

        save_path, _ = QFileDialog.getSaveFileName(self, "Guardar Archivo", blob.name.split('/')[-1])
        if save_path:
            import uuid
            
            # Registrar en TransferManager
            transfer_id = self.transfer_manager.create_transfer(
                TransferType.GCP_DOWNLOAD,
                blob.name,
                f"gcp://{self.current_bucket.name}/{blob.name}", 
                save_path, 
                blob.size or 0
            )
            
            # Usar GCPDownloadWorker integrado
            worker = GCPDownloadWorker(blob, save_path, transfer_id)
            # Ya no necesitamos conectar progress, el worker actualiza el manager
            worker.finished.connect(lambda s, m: self.cleanup_worker(worker))
            
            self.active_workers.add(worker)
            worker.start()
            
            self.connection_status.setText(f"🚀 Iniciando descarga de {blob.name}...")

    def _download_thread(self, blob, save_path):
        # Legacy stub
        blob.download_to_filename(save_path)
        return True

    # Metodos legacy eliminados (update_download_progress, on_download_finished)
