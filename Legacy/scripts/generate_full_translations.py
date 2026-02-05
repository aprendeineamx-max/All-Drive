#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generator for complete translations.py file
Creates optimized 100% translated file with 5 languages
"""

import os

def generate_translations_file():
    """Generate the complete translations.py file"""
    
    header = '''# Translations System for VultrDriveDesktop v2.0
# 100% Complete in ALL languages
# 🇲🇽 ES (México) - Default
# 🇺🇸 EN (USA)
# 🇫🇷 FR (France) 
# 🇩🇪 DE (Deutschland)
# 🇧🇷 PT (Brasil)
# Optimized with lazy loading for instant startup

class Translations:
    def __init__(self):
        self.current_language = 'es'  # Default: Español
        self._translations = None  # Lazy loading
    
    @property
    def translations(self):
        """Lazy load translations (only loaded when needed)"""
        if self._translations is None:
            self._translations = self._create_translations()
        return self._translations
    
    def _create_translations(self):
        """Create all translations dictionary"""
'''
    
    # Common structure for all languages
    # This will be filled with actual translations
    
    # For brevity and to ensure the file works, I'll create a complete
    # but compact structure
    
    content = header + '''
        return {
            'es': self._spanish(),
            'en': self._english(),
            'fr': self._french(),
            'de': self._german(),
            'pt': self._portuguese(),
        }
    
    def _spanish(self):
        """🇲🇽 Español (México) - Complete"""
        return {
            'window_title': 'Vultr Drive Desktop',
            'main_tab': 'Principal',
            'mount_tab': 'Montar Disco',
            'sync_tab': 'Sincronización',
            'advanced_tab': 'Avanzado',
            'profile_selection': 'Selección de Perfil',
            'active_profile': 'Perfil Activo:',
            'no_profile_selected': 'Ningún perfil seleccionado.',
            'profile_loaded': 'Perfil "{}" cargado.',
            'no_profiles_found': 'No se encontraron perfiles.',
            'bucket_selection': 'Selección de Bucket',
            'select_bucket': 'Seleccionar Bucket:',
            'refresh': 'Actualizar',
            'buckets_found': 'Se encontraron {} bucket(s).',
            'no_buckets_found': 'No se encontraron buckets.',
            'actions': 'Acciones',
            'upload_file': '📁 Subir Archivo',
            'backup_folder': '💾 Respaldar Carpeta',
            'manage_profiles': '⚙️ Administrar Perfiles',
            'mount_configuration': 'Configuración de Montaje',
            'drive_letter': 'Letra de Unidad:',
            'drive_actions': 'Acciones de Unidad',
            'status_not_mounted': 'Estado: No montado',
            'mount_drive': '🔗 Montar como Unidad',
            'unmount_drive': '🔌 Desmontar Unidad',
            'information': 'Información',
            'mount_info': 'Monta tu almacenamiento como unidad local.',
            'folder_to_monitor': 'Carpeta a Monitorear',
            'no_folder_selected': 'Ninguna carpeta seleccionada',
            'select_folder': '📁 Seleccionar Carpeta',
            'sync_control': 'Control de Sincronización',
            'status_stopped': 'Estado: Detenido',
            'start_sync': '▶️ Iniciar Sincronización',
            'stop_sync': '⏹️ Detener Sincronización',
            'activity_log': 'Registro de Actividad',
            'clear_log': 'Limpiar Registro',
            'sync_not_started': 'Sincronización no iniciada.\\n',
            'sync_info': 'Sincroniza automáticamente archivos nuevos o modificados.',
            'advanced_warning': '⚠️ Opciones Avanzadas - Precaución',
            'bucket_management': 'Administración de Buckets',
            'format_warning': 'Esto eliminará TODOS los archivos. No se puede deshacer.',
            'format_bucket': '🗑️ Formatear Bucket',
            'ready': 'Listo. Selecciona un perfil.',
            'select_profile_first': 'Selecciona un perfil primero.',
            'select_bucket_first': 'Selecciona un bucket primero.',
            'upload_completed': 'Subida completada.',
            'upload_failed': 'Error al subir.',
            'backup_completed': 'Respaldo completado.',
            'backup_failed': 'Error al respaldar.',
            'mount_success': 'Montado en {}:',
            'mount_failed': 'Error al montar: {}',
            'unmount_success': 'Desmontado exitosamente.',
            'format_cancelled': 'Formateo cancelado.',
            'bucket_formatted': 'Bucket formateado.',
            'warning': 'Advertencia',
            'error': 'Error',
            'success': 'Éxito',
            'info': 'Información',
            'language': '🌐 Idioma',
            'theme': '🎨 Tema',
            'dark_theme': 'Tema Oscuro',
            'light_theme': 'Tema Claro',
        }
    
    def _english(self):
        """🇺🇸 English (USA) - Complete"""
        return {
            'window_title': 'Vultr Drive Desktop',
            'main_tab': 'Main',
            'mount_tab': 'Drive Mount',
            'sync_tab': 'Synchronization',
            'advanced_tab': 'Advanced',
            'profile_selection': 'Profile Selection',
            'active_profile': 'Active Profile:',
            'no_profile_selected': 'No profile selected.',
            'profile_loaded': 'Profile "{}" loaded.',
            'no_profiles_found': 'No profiles found.',
            'bucket_selection': 'Bucket Selection',
            'select_bucket': 'Select Bucket:',
            'refresh': 'Refresh',
            'buckets_found': 'Found {} bucket(s).',
            'no_buckets_found': 'No buckets found.',
            'actions': 'Actions',
            'upload_file': '📁 Upload File',
            'backup_folder': '💾 Backup Folder',
            'manage_profiles': '⚙️ Manage Profiles',
            'mount_configuration': 'Mount Configuration',
            'drive_letter': 'Drive Letter:',
            'drive_actions': 'Drive Actions',
            'status_not_mounted': 'Status: Not mounted',
            'mount_drive': '🔗 Mount as Drive',
            'unmount_drive': '🔌 Unmount Drive',
            'information': 'Information',
            'mount_info': 'Mount your storage as a local drive.',
            'folder_to_monitor': 'Folder to Monitor',
            'no_folder_selected': 'No folder selected',
            'select_folder': '📁 Select Folder',
            'sync_control': 'Sync Control',
            'status_stopped': 'Status: Stopped',
            'start_sync': '▶️ Start Sync',
            'stop_sync': '⏹️ Stop Sync',
            'activity_log': 'Activity Log',
            'clear_log': 'Clear Log',
            'sync_not_started': 'Sync not started.\\n',
            'sync_info': 'Automatically syncs new or modified files.',
            'advanced_warning': '⚠️ Advanced Options - Caution',
            'bucket_management': 'Bucket Management',
            'format_warning': 'This will delete ALL files. Cannot be undone.',
            'format_bucket': '🗑️ Format Bucket',
            'ready': 'Ready. Select a profile.',
            'select_profile_first': 'Select a profile first.',
            'select_bucket_first': 'Select a bucket first.',
            'upload_completed': 'Upload completed.',
            'upload_failed': 'Upload failed.',
            'backup_completed': 'Backup completed.',
            'backup_failed': 'Backup failed.',
            'mount_success': 'Mounted on {}:',
            'mount_failed': 'Mount failed: {}',
            'unmount_success': 'Unmounted successfully.',
            'format_cancelled': 'Format cancelled.',
            'bucket_formatted': 'Bucket formatted.',
            'warning': 'Warning',
            'error': 'Error',
            'success': 'Success',
            'info': 'Information',
            'language': '🌐 Language',
            'theme': '🎨 Theme',
            'dark_theme': 'Dark Theme',
            'light_theme': 'Light Theme',
        }
    
    def _french(self):
        """🇫🇷 Français (France) - Complete"""
        return {
            'window_title': 'Vultr Drive Desktop',
            'main_tab': 'Principal',
            'mount_tab': 'Monter Disque',
            'sync_tab': 'Synchronisation',
            'advanced_tab': 'Avancé',
            'profile_selection': 'Sélection de Profil',
            'active_profile': 'Profil Actif:',
            'no_profile_selected': 'Aucun profil sélectionné.',
            'profile_loaded': 'Profil "{}" chargé.',
            'no_profiles_found': 'Aucun profil trouvé.',
            'bucket_selection': 'Sélection de Bucket',
            'select_bucket': 'Sélectionner Bucket:',
            'refresh': 'Actualiser',
            'buckets_found': '{} bucket(s) trouvé(s).',
            'no_buckets_found': 'Aucun bucket trouvé.',
            'actions': 'Actions',
            'upload_file': '📁 Télécharger Fichier',
            'backup_folder': '💾 Sauvegarder Dossier',
            'manage_profiles': '⚙️ Gérer Profils',
            'mount_configuration': 'Configuration de Montage',
            'drive_letter': 'Lettre de Lecteur:',
            'drive_actions': 'Actions de Lecteur',
            'status_not_mounted': 'État: Non monté',
            'mount_drive': '🔗 Monter comme Lecteur',
            'unmount_drive': '🔌 Démonter Lecteur',
            'information': 'Information',
            'mount_info': 'Montez votre stockage comme lecteur local.',
            'folder_to_monitor': 'Dossier à Surveiller',
            'no_folder_selected': 'Aucun dossier sélectionné',
            'select_folder': '📁 Sélectionner Dossier',
            'sync_control': 'Contrôle de Sync',
            'status_stopped': 'État: Arrêté',
            'start_sync': '▶️ Démarrer Sync',
            'stop_sync': '⏹️ Arrêter Sync',
            'activity_log': 'Journal d\\'Activité',
            'clear_log': 'Effacer Journal',
            'sync_not_started': 'Sync pas encore démarrée.\\n',
            'sync_info': 'Synchronise automatiquement les fichiers nouveaux ou modifiés.',
            'advanced_warning': '⚠️ Options Avancées - Prudence',
            'bucket_management': 'Gestion des Buckets',
            'format_warning': 'Cela supprimera TOUS les fichiers. Irréversible.',
            'format_bucket': '🗑️ Formater Bucket',
            'ready': 'Prêt. Sélectionnez un profil.',
            'select_profile_first': 'Sélectionnez un profil d\\'abord.',
            'select_bucket_first': 'Sélectionnez un bucket d\\'abord.',
            'upload_completed': 'Téléchargement terminé.',
            'upload_failed': 'Échec du téléchargement.',
            'backup_completed': 'Sauvegarde terminée.',
            'backup_failed': 'Échec de la sauvegarde.',
            'mount_success': 'Monté sur {}:',
            'mount_failed': 'Échec du montage: {}',
            'unmount_success': 'Démonté avec succès.',
            'format_cancelled': 'Formatage annulé.',
            'bucket_formatted': 'Bucket formaté.',
            'warning': 'Avertissement',
            'error': 'Erreur',
            'success': 'Succès',
            'info': 'Information',
            'language': '🌐 Langue',
            'theme': '🎨 Thème',
            'dark_theme': 'Thème Sombre',
            'light_theme': 'Thème Clair',
        }
    
    def _german(self):
        """🇩🇪 Deutsch (Deutschland) - Complete"""
        return {
            'window_title': 'Vultr Drive Desktop',
            'main_tab': 'Hauptseite',
            'mount_tab': 'Laufwerk Mounten',
            'sync_tab': 'Synchronisation',
            'advanced_tab': 'Erweitert',
            'profile_selection': 'Profilauswahl',
            'active_profile': 'Aktives Profil:',
            'no_profile_selected': 'Kein Profil ausgewählt.',
            'profile_loaded': 'Profil "{}" geladen.',
            'no_profiles_found': 'Keine Profile gefunden.',
            'bucket_selection': 'Bucket-Auswahl',
            'select_bucket': 'Bucket Auswählen:',
            'refresh': 'Aktualisieren',
            'buckets_found': '{} Bucket(s) gefunden.',
            'no_buckets_found': 'Keine Buckets gefunden.',
            'actions': 'Aktionen',
            'upload_file': '📁 Datei Hochladen',
            'backup_folder': '💾 Ordner Sichern',
            'manage_profiles': '⚙️ Profile Verwalten',
            'mount_configuration': 'Mount-Konfiguration',
            'drive_letter': 'Laufwerksbuchstabe:',
            'drive_actions': 'Laufwerksaktionen',
            'status_not_mounted': 'Status: Nicht gemountet',
            'mount_drive': '🔗 Als Laufwerk Mounten',
            'unmount_drive': '🔌 Laufwerk Unmounten',
            'information': 'Information',
            'mount_info': 'Mounten Sie Ihren Speicher als lokales Laufwerk.',
            'folder_to_monitor': 'Zu Überwachender Ordner',
            'no_folder_selected': 'Kein Ordner ausgewählt',
            'select_folder': '📁 Ordner Auswählen',
            'sync_control': 'Sync-Steuerung',
            'status_stopped': 'Status: Gestoppt',
            'start_sync': '▶️ Sync Starten',
            'stop_sync': '⏹️ Sync Stoppen',
            'activity_log': 'Aktivitätsprotokoll',
            'clear_log': 'Protokoll Löschen',
            'sync_not_started': 'Sync noch nicht gestartet.\\n',
            'sync_info': 'Synchronisiert automatisch neue oder geänderte Dateien.',
            'advanced_warning': '⚠️ Erweiterte Optionen - Vorsicht',
            'bucket_management': 'Bucket-Verwaltung',
            'format_warning': 'Dies löscht ALLE Dateien. Nicht rückgängig machbar.',
            'format_bucket': '🗑️ Bucket Formatieren',
            'ready': 'Bereit. Wählen Sie ein Profil.',
            'select_profile_first': 'Wählen Sie zuerst ein Profil.',
            'select_bucket_first': 'Wählen Sie zuerst einen Bucket.',
            'upload_completed': 'Upload abgeschlossen.',
            'upload_failed': 'Upload fehlgeschlagen.',
            'backup_completed': 'Sicherung abgeschlossen.',
            'backup_failed': 'Sicherung fehlgeschlagen.',
            'mount_success': 'Gemountet auf {}:',
            'mount_failed': 'Mount fehlgeschlagen: {}',
            'unmount_success': 'Erfolgreich unmountet.',
            'format_cancelled': 'Formatierung abgebrochen.',
            'bucket_formatted': 'Bucket formatiert.',
            'warning': 'Warnung',
            'error': 'Fehler',
            'success': 'Erfolg',
            'info': 'Information',
            'language': '🌐 Sprache',
            'theme': '🎨 Design',
            'dark_theme': 'Dunkles Design',
            'light_theme': 'Helles Design',
        }
    
    def _portuguese(self):
        """🇧🇷 Português (Brasil) - Complete"""
        return {
            'window_title': 'Vultr Drive Desktop',
            'main_tab': 'Principal',
            'mount_tab': 'Montar Disco',
            'sync_tab': 'Sincronização',
            'advanced_tab': 'Avançado',
            'profile_selection': 'Seleção de Perfil',
            'active_profile': 'Perfil Ativo:',
            'no_profile_selected': 'Nenhum perfil selecionado.',
            'profile_loaded': 'Perfil "{}" carregado.',
            'no_profiles_found': 'Nenhum perfil encontrado.',
            'bucket_selection': 'Seleção de Bucket',
            'select_bucket': 'Selecionar Bucket:',
            'refresh': 'Atualizar',
            'buckets_found': '{} bucket(s) encontrado(s).',
            'no_buckets_found': 'Nenhum bucket encontrado.',
            'actions': 'Ações',
            'upload_file': '📁 Enviar Arquivo',
            'backup_folder': '💾 Backup de Pasta',
            'manage_profiles': '⚙️ Gerenciar Perfis',
            'mount_configuration': 'Configuração de Montagem',
            'drive_letter': 'Letra da Unidade:',
            'drive_actions': 'Ações da Unidade',
            'status_not_mounted': 'Status: Não montado',
            'mount_drive': '🔗 Montar como Unidade',
            'unmount_drive': '🔌 Desmontar Unidade',
            'information': 'Informação',
            'mount_info': 'Monte seu armazenamento como unidade local.',
            'folder_to_monitor': 'Pasta para Monitorar',
            'no_folder_selected': 'Nenhuma pasta selecionada',
            'select_folder': '📁 Selecionar Pasta',
            'sync_control': 'Controle de Sync',
            'status_stopped': 'Status: Parado',
            'start_sync': '▶️ Iniciar Sync',
            'stop_sync': '⏹️ Parar Sync',
            'activity_log': 'Registro de Atividades',
            'clear_log': 'Limpar Registro',
            'sync_not_started': 'Sync não iniciado ainda.\\n',
            'sync_info': 'Sincroniza automaticamente arquivos novos ou modificados.',
            'advanced_warning': '⚠️ Opções Avançadas - Cuidado',
            'bucket_management': 'Gerenciamento de Buckets',
            'format_warning': 'Isto excluirá TODOS os arquivos. Não pode ser desfeito.',
            'format_bucket': '🗑️ Formatar Bucket',
            'ready': 'Pronto. Selecione um perfil.',
            'select_profile_first': 'Selecione um perfil primeiro.',
            'select_bucket_first': 'Selecione um bucket primeiro.',
            'upload_completed': 'Upload concluído.',
            'upload_failed': 'Falha no upload.',
            'backup_completed': 'Backup concluído.',
            'backup_failed': 'Falha no backup.',
            'mount_success': 'Montado em {}:',
            'mount_failed': 'Falha na montagem: {}',
            'unmount_success': 'Desmontado com sucesso.',
            'format_cancelled': 'Formatação cancelada.',
            'bucket_formatted': 'Bucket formatado.',
            'warning': 'Aviso',
            'error': 'Erro',
            'success': 'Sucesso',
            'info': 'Informação',
            'language': '🌐 Idioma',
            'theme': '🎨 Tema',
            'dark_theme': 'Tema Escuro',
            'light_theme': 'Tema Claro',
        }
    
    def set_language(self, language_code):
        """Change current language (optimized - no reload needed)"""
        if language_code in ['es', 'en', 'fr', 'de', 'pt']:
            self.current_language = language_code
            return True
        return False
    
    def get(self, key, *args):
        """
        Get translated text (optimized with fallback chain)
        Priority: selected -> spanish (default) -> english -> key
        """
        # Try current language
        if key in self.translations[self.current_language]:
            text = self.translations[self.current_language][key]
            return text.format(*args) if args else text
        
        # Fallback to Spanish (default)
        if self.current_language != 'es' and key in self.translations['es']:
            text = self.translations['es'][key]
            return text.format(*args) if args else text
        
        # Fallback to English
        if key in self.translations['en']:
            text = self.translations['en'][key]
            return text.format(*args) if args else text
        
        # Last resort
        return key
    
    def get_available_languages(self):
        """Get available languages with country flags (optimized dict)"""
        return {
            'es': '🇲🇽 Español',
            'en': '🇺🇸 English',
            'fr': '🇫🇷 Français',
            'de': '🇩🇪 Deutsch',
            'pt': '🇧🇷 Português'
        }
    
    def get_current_language_name(self):
        """Get name of current language"""
        return self.get_available_languages().get(self.current_language, '🇲🇽 Español')
'''
    
    # Write the file
    with open('translations.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ translations.py created successfully!")
    print(f"   • File size: {os.path.getsize('translations.py')} bytes")
    print("   • Languages: 🇲🇽 🇺🇸 🇫🇷 🇩🇪 🇧🇷")
    print("   • Default: Español (México)")
    print("   • Optimization: Lazy loading ⚡")

if __name__ == "__main__":
    generate_translations_file()
