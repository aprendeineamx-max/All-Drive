import sys
import os
from PyQt6.QtWidgets import QApplication, QMessageBox, QFileDialog
from config_manager import ConfigManager
from s3_handler import S3Handler

def backup_now():
    """Quick backup script for desktop shortcut"""
    app = QApplication(sys.argv)
    
    config_manager = ConfigManager()
    profiles = config_manager.list_profiles()
    
    if not profiles:
        QMessageBox.critical(None, "Error", "No profiles configured. Please configure a profile first.")
        return
    
    # Use first profile by default
    profile_name = profiles[0]
    config = config_manager.get_config(profile_name)
    
    if not config:
        QMessageBox.critical(None, "Error", "Failed to load profile configuration.")
        return
    
    s3_handler = S3Handler(config['access_key'], config['secret_key'], config['host_base'])
    buckets = s3_handler.list_buckets()
    
    if not buckets:
        QMessageBox.critical(None, "Error", "No buckets found. Please create a bucket first.")
        return
    
    # Select folder to backup
    folder = QFileDialog.getExistingDirectory(None, "Select Folder to Backup Now")
    
    if not folder:
        return
    
    # Count files
    file_count = sum([len(files) for r, d, files in os.walk(folder)])
    
    reply = QMessageBox.question(
        None,
        "Confirm Backup",
        f"Ready to backup {file_count} files from:\n{folder}\n\nTo bucket: {buckets[0]}\n\nContinue?",
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
    )
    
    if reply == QMessageBox.StandardButton.No:
        return
    
    # Perform backup
    uploaded = 0
    errors = 0
    
    for root, dirs, files in os.walk(folder):
        for file in files:
            file_path = os.path.join(root, file)
            relative_path = os.path.relpath(file_path, folder)
            
            if s3_handler.upload_file(buckets[0], file_path, relative_path):
                uploaded += 1
            else:
                errors += 1
    
    QMessageBox.information(
        None,
        "Backup Complete",
        f"Backup completed!\n\nUploaded: {uploaded} files\nErrors: {errors}"
    )

if __name__ == '__main__':
    backup_now()
