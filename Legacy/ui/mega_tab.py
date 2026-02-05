from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QGroupBox, QListWidget, 
                             QMessageBox, QFormLayout, QListWidgetItem, QTextEdit,
                             QProgressBar, QScrollArea, QSplitter, QTableWidget,
                             QTableWidgetItem, QHeaderView, QFrame)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QIcon, QColor, QFont
import time


class BulkImportWorker(QThread):
    """Worker thread para importar cuentas masivamente sin bloquear la UI"""
    account_processed = pyqtSignal(str, str, bool, str)  # email, profile_name, success, message
    all_finished = pyqtSignal(int, int)  # total_success, total_failed
    
    def __init__(self, rclone_manager, accounts):
        super().__init__()
        self.rclone_manager = rclone_manager
        self.accounts = accounts  # Lista de tuplas (email, password)
    
    def run(self):
        success_count = 0
        fail_count = 0
        
        for email, password in self.accounts:
            # Generar nombre de perfil desde el email (parte antes del @)
            profile_name = email.split('@')[0].replace('.', '_').replace('-', '_')
            
            # Intentar crear la config
            success, message = self.rclone_manager.create_mega_config(profile_name, email, password)
            
            if success:
                # Validar que realmente funcione intentando listar
                try:
                    validation_msg = self._validate_account(profile_name)
                    if validation_msg:
                        message = validation_msg
                        success = False
                        fail_count += 1
                    else:
                        success_count += 1
                        message = "✅ Vinculada y verificada correctamente"
                except Exception as e:
                    message = f"⚠️ Creada pero no verificada: {str(e)}"
                    success_count += 1  # Cuenta como éxito pero con advertencia
            else:
                fail_count += 1
                message = f"❌ {message}"
            
            self.account_processed.emit(email, profile_name, success, message)
            time.sleep(0.5)  # Pequeña pausa entre cuentas para no saturar
        
        self.all_finished.emit(success_count, fail_count)
    
    def _validate_account(self, profile_name):
        """Intenta validar que la cuenta funcione listando su contenido"""
        import subprocess
        import sys
        
        rclone_path = self.rclone_manager._find_rclone_executable()
        if not rclone_path:
            return "Rclone no encontrado"
        
        cmd = [
            rclone_path,
            "lsd",
            f"{profile_name}:",
            "--config", self.rclone_manager.rclone_config_file,
            "--contimeout", "10s",
            "--timeout", "15s"
        ]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=20,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
            )
            
            if result.returncode != 0:
                stderr = result.stderr.lower()
                if "wrong" in stderr or "password" in stderr or "invalid" in stderr:
                    return "❌ Credenciales incorrectas (email o contraseña)"
                elif "blocked" in stderr or "suspended" in stderr:
                    return "❌ Cuenta bloqueada o suspendida por MEGA"
                elif "timeout" in stderr:
                    return "⚠️ Tiempo de espera agotado - verificar conexión"
                elif "2fa" in stderr or "two-factor" in stderr:
                    return "❌ Cuenta requiere autenticación de 2 factores"
                else:
                    return f"❌ Error: {result.stderr[:100]}"
            
            return None  # Sin error = éxito
        except subprocess.TimeoutExpired:
            return "⚠️ Tiempo de espera agotado"
        except Exception as e:
            return f"⚠️ Error de validación: {str(e)}"


class MegaTab(QWidget):
    def __init__(self, rclone_manager, main_window):
        super().__init__()
        self.rclone_manager = rclone_manager
        self.main_window = main_window
        self.import_worker = None
        self.init_ui()

    def init_ui(self):
        # Layout principal de la pestaña (contendrá el scroll)
        # Check if layout exists to prevent crash
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
        header_label = QLabel("☁️ Gestión de Cuentas MEGA.nz")
        header_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #e74c3c;")
        layout.addWidget(header_label)

        # Splitter para dividir la UI
        splitter = QSplitter(Qt.Orientation.Vertical)
        
        # ===== SECCIÓN 1: Agregar cuenta individual =====
        single_widget = QWidget()
        single_layout = QVBoxLayout(single_widget)
        single_layout.setContentsMargins(0, 0, 0, 0)
        
        form_group = QGroupBox("➕ Agregar Cuenta Individual")
        form_layout = QFormLayout()
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Ej: MiMegaPersonal")
        
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("correo@ejemplo.com")
        
        self.pass_input = QLineEdit()
        self.pass_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.pass_input.setPlaceholderText("Contraseña de MEGA")
        
        form_layout.addRow("Nombre del Perfil:", self.name_input)
        form_layout.addRow("Correo Electrónico:", self.email_input)
        form_layout.addRow("Contraseña:", self.pass_input)
        
        add_btn = QPushButton("➕ Agregar Cuenta MEGA")
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #d32f2f;
                color: white;
                font-weight: bold;
                padding: 8px;
                border-radius: 4px;
            }
            QPushButton:hover { background-color: #b71c1c; }
        """)
        add_btn.clicked.connect(self.add_account)
        form_layout.addRow(add_btn)
        
        form_group.setLayout(form_layout)
        single_layout.addWidget(form_group)
        splitter.addWidget(single_widget)

        # ===== SECCIÓN 2: Importación Masiva =====
        bulk_widget = QWidget()
        bulk_layout = QVBoxLayout(bulk_widget)
        bulk_layout.setContentsMargins(0, 0, 0, 0)
        
        bulk_group = QGroupBox("📥 Importación Masiva de Cuentas")
        bulk_inner = QVBoxLayout()
        
        # Instrucciones
        instructions = QLabel(
            "📋 Pega aquí tus cuentas en formato: <b>email[TAB]contraseña</b> (una por línea)\n"
            "Ejemplo: usuario@email.com    contraseña123"
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet("color: #95a5a6; padding: 5px;")
        bulk_inner.addWidget(instructions)
        
        # Área de texto para pegar cuentas
        self.bulk_input = QTextEdit()
        self.bulk_input.setPlaceholderText(
            "usuario1@email.com\tcontraseña1\n"
            "usuario2@email.com\tcontraseña2\n"
            "usuario3@email.com\tcontraseña3"
        )
        self.bulk_input.setMaximumHeight(120)
        self.bulk_input.setStyleSheet("""
            QTextEdit {
                background-color: #1a1a2e;
                border: 1px solid #34495e;
                border-radius: 5px;
                padding: 10px;
                font-family: 'Consolas', monospace;
            }
        """)
        bulk_inner.addWidget(self.bulk_input)
        
        # Botones de importación
        import_buttons = QHBoxLayout()
        
        self.import_btn = QPushButton("🚀 Importar y Vincular Cuentas")
        self.import_btn.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6;
                color: white;
                font-weight: bold;
                padding: 12px 20px;
                border-radius: 5px;
                font-size: 13px;
            }
            QPushButton:hover { background-color: #8e44ad; }
            QPushButton:disabled { background-color: #7f8c8d; }
        """)
        self.import_btn.clicked.connect(self.start_bulk_import)
        import_buttons.addWidget(self.import_btn)
        
        clear_btn = QPushButton("🗑️ Limpiar")
        clear_btn.setStyleSheet("background-color: #555;")
        clear_btn.clicked.connect(lambda: self.bulk_input.clear())
        import_buttons.addWidget(clear_btn)
        
        bulk_inner.addLayout(import_buttons)
        
        # Barra de progreso
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: none;
                border-radius: 5px;
                background-color: #34495e;
                height: 20px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #27ae60;
                border-radius: 5px;
            }
        """)
        bulk_inner.addWidget(self.progress_bar)
        
        # Tabla de resultados
        results_label = QLabel("📊 Resultados de Importación:")
        results_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        bulk_inner.addWidget(results_label)
        
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(4)
        self.results_table.setHorizontalHeaderLabels(["Estado", "Email", "Perfil", "Mensaje"])
        self.results_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.results_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.results_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.results_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self.results_table.setAlternatingRowColors(True)
        self.results_table.setStyleSheet("""
            QTableWidget {
                background-color: #1a1a2e;
                alternate-background-color: #252542;
                gridline-color: #34495e;
            }
            QHeaderView::section {
                background-color: #2c3e50;
                padding: 8px;
                border: none;
                font-weight: bold;
            }
        """)
        bulk_inner.addWidget(self.results_table)
        
        bulk_group.setLayout(bulk_inner)
        bulk_layout.addWidget(bulk_group)
        splitter.addWidget(bulk_widget)

        # ===== SECCIÓN 3: Lista de cuentas configuradas =====
        list_widget = QWidget()
        list_layout_container = QVBoxLayout(list_widget)
        list_layout_container.setContentsMargins(0, 0, 0, 0)
        
        list_group = QGroupBox("📂 Cuentas Configuradas")
        list_layout = QVBoxLayout()
        
        self.accounts_list = QListWidget()
        self.accounts_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self.accounts_list.setMaximumHeight(150)
        list_layout.addWidget(self.accounts_list)
        
        actions_layout = QHBoxLayout()
        
        refresh_btn = QPushButton("🔄 Actualizar")
        refresh_btn.clicked.connect(self.load_accounts)
        
        validate_btn = QPushButton("✅ Validar Seleccionada")
        validate_btn.setStyleSheet("background-color: #27ae60;")
        validate_btn.clicked.connect(self.validate_selected_account)
        
        delete_btn = QPushButton("🗑️ Eliminar")
        delete_btn.setStyleSheet("background-color: #e74c3c;")
        delete_btn.clicked.connect(self.delete_account)
        
        actions_layout.addWidget(refresh_btn)
        actions_layout.addWidget(validate_btn)
        actions_layout.addWidget(delete_btn)
        list_layout.addLayout(actions_layout)
        
        list_group.setLayout(list_layout)
        list_layout_container.addWidget(list_group)
        splitter.addWidget(list_widget)

        # self.setLayout(layout) # Removed

        # Configurar tamaños del splitter
        splitter.setSizes([150, 350, 150])
        layout.addWidget(splitter, 1)

        # Finalizar setup del scroll
        scroll.setWidget(content_widget)
        main_layout.addWidget(scroll)
        self.load_accounts()

    def add_account(self):
        name = self.name_input.text().strip()
        user = self.email_input.text().strip()
        password = self.pass_input.text().strip()
        
        if not name or not user or not password:
            QMessageBox.warning(self, "Campos incompletos", "Por favor completa todos los campos.")
            return
            
        if " " in name:
            QMessageBox.warning(self, "Nombre Invalido", "El nombre del perfil no debe contener espacios.")
            return

        success, msg = self.rclone_manager.create_mega_config(name, user, password)
        
        if success:
            QMessageBox.information(self, "Éxito", msg)
            self.name_input.clear()
            self.email_input.clear()
            self.pass_input.clear()
            self.load_accounts()
        else:
            QMessageBox.critical(self, "Error", msg)

    def start_bulk_import(self):
        """Inicia la importación masiva de cuentas"""
        text = self.bulk_input.toPlainText().strip()
        if not text:
            QMessageBox.warning(self, "Sin datos", "Por favor pega las cuentas a importar.")
            return
        
        # Parsear las líneas
        accounts = []
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        
        # Detectar formato automáticamente
        # Formato 1: email[TAB]contraseña en la misma línea
        # Formato 2: líneas alternas (email en una línea, contraseña en la siguiente)
        
        # Verificar si la primera línea tiene tab o espacios múltiples (formato 1)
        first_line = lines[0] if lines else ""
        is_same_line_format = '\t' in first_line or '    ' in first_line or '  ' in first_line
        
        if is_same_line_format:
            # Formato: email[TAB]contraseña o email    contraseña
            for line in lines:
                parts = line.split('\t')
                if len(parts) != 2:
                    parts = line.split('    ')  # 4 espacios
                if len(parts) != 2:
                    parts = line.split('  ')  # 2 espacios
                
                if len(parts) == 2:
                    email = parts[0].strip()
                    password = parts[1].strip()
                    if email and password and '@' in email:
                        accounts.append((email, password))
        else:
            # Formato: líneas alternas (email en línea impar, contraseña en línea par)
            # También soporta: detectar automáticamente cuál es email (tiene @)
            i = 0
            while i < len(lines):
                current_line = lines[i]
                
                # Si la línea actual tiene @, es un email
                if '@' in current_line:
                    email = current_line
                    # La siguiente línea es la contraseña
                    if i + 1 < len(lines):
                        password = lines[i + 1]
                        # Verificar que la contraseña no sea otro email
                        if '@' not in password or not any(c in password for c in ['.com', '.org', '.net', '.co']):
                            accounts.append((email, password))
                            i += 2
                            continue
                i += 1
        
        if not accounts:
            QMessageBox.warning(
                self, 
                "Formato inválido", 
                "No se pudieron parsear las cuentas.\n\n"
                "Formatos soportados:\n"
                "1) email[TAB]contraseña (en la misma línea)\n"
                "2) email en una línea, contraseña en la siguiente\n\n"
                f"Se detectaron {len(lines)} líneas pero ninguna cuenta válida."
            )
            return
        
        # Limpiar tabla de resultados
        self.results_table.setRowCount(0)
        
        # Configurar UI para importación
        self.import_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setMaximum(len(accounts))
        self.progress_bar.setValue(0)
        
        # Iniciar worker thread
        self.import_worker = BulkImportWorker(self.rclone_manager, accounts)
        self.import_worker.account_processed.connect(self._on_account_processed)
        self.import_worker.all_finished.connect(self._on_bulk_import_finished)
        self.import_worker.start()

    def _on_account_processed(self, email, profile_name, success, message):
        """Callback cuando se procesa una cuenta"""
        row = self.results_table.rowCount()
        self.results_table.insertRow(row)
        
        # Estado (icono)
        status_item = QTableWidgetItem("✅" if success else "❌")
        status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        if success:
            status_item.setBackground(QColor("#1e5631"))
        else:
            status_item.setBackground(QColor("#5e1e1e"))
        
        # Email
        email_item = QTableWidgetItem(email)
        
        # Perfil generado
        profile_item = QTableWidgetItem(profile_name)
        
        # Mensaje de estado
        msg_item = QTableWidgetItem(message)
        if not success:
            msg_item.setForeground(QColor("#e74c3c"))
        else:
            msg_item.setForeground(QColor("#27ae60"))
        
        self.results_table.setItem(row, 0, status_item)
        self.results_table.setItem(row, 1, email_item)
        self.results_table.setItem(row, 2, profile_item)
        self.results_table.setItem(row, 3, msg_item)
        
        # Actualizar progreso
        self.progress_bar.setValue(row + 1)
        
        # Scroll al final
        self.results_table.scrollToBottom()

    def _on_bulk_import_finished(self, success_count, fail_count):
        """Callback cuando termina la importación masiva"""
        self.import_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.load_accounts()
        
        # Mostrar resumen
        total = success_count + fail_count
        QMessageBox.information(
            self,
            "Importación Completada",
            f"📊 Resumen de importación:\n\n"
            f"✅ Exitosas: {success_count}\n"
            f"❌ Fallidas: {fail_count}\n"
            f"📝 Total: {total}\n\n"
            f"Revisa la tabla de resultados para más detalles."
        )

    def validate_selected_account(self):
        """Valida la cuenta seleccionada en la lista"""
        current_item = self.accounts_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Sin selección", "Selecciona una cuenta para validar.")
            return
        
        profile_name = current_item.data(Qt.ItemDataRole.UserRole)
        
        # Mostrar mensaje de espera
        self.main_window.statusBar().showMessage(f"Validando cuenta {profile_name}...")
        
        # Validar usando el método del worker
        worker = BulkImportWorker(self.rclone_manager, [])
        error = worker._validate_account(profile_name)
        
        if error:
            QMessageBox.warning(
                self, 
                "Validación Fallida",
                f"❌ La cuenta '{profile_name}' tiene problemas:\n\n{error}\n\n"
                f"💡 Posibles soluciones:\n"
                f"• Verifica que el email y contraseña sean correctos\n"
                f"• Asegúrate de que la cuenta no esté bloqueada\n"
                f"• Comprueba tu conexión a internet\n"
                f"• Si tiene 2FA activado, desactívalo o usa contraseña de app"
            )
        else:
            QMessageBox.information(
                self,
                "Validación Exitosa",
                f"✅ La cuenta '{profile_name}' está activa y funcionando correctamente."
            )
        
        self.main_window.statusBar().showMessage("Listo", 3000)

    def load_accounts(self):
        self.accounts_list.clear()
        profiles = self.rclone_manager.list_mega_profiles()
        for p in profiles:
            item = QListWidgetItem(f"☁️ {p['name']} ({p['user']})")
            item.setData(Qt.ItemDataRole.UserRole, p['name'])
            self.accounts_list.addItem(item)

    def delete_account(self):
        current_item = self.accounts_list.currentItem()
        if not current_item:
            return
            
        profile_name = current_item.data(Qt.ItemDataRole.UserRole)
        
        reply = QMessageBox.question(
            self, 
            "Confirmar Eliminación",
            f"¿Estás seguro de eliminar el perfil '{profile_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            success, msg = self.rclone_manager.delete_rclone_profile(profile_name)
            if success:
                self.load_accounts()
            else:
                QMessageBox.critical(self, "Error", msg)
