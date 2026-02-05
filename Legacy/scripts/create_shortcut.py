import os
import winshell
from win32com.client import Dispatch

def create_backup_shortcut():
    """Create a desktop shortcut for quick backup"""
    desktop = winshell.desktop()
    
    # Path to the Python executable and script
    python_exe = os.path.join(os.path.dirname(os.sys.executable), "pythonw.exe")
    script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backup_now.py")
    
    # Create shortcut
    shortcut_path = os.path.join(desktop, "Vultr Backup Now.lnk")
    
    shell = Dispatch('WScript.Shell')
    shortcut = shell.CreateShortCut(shortcut_path)
    shortcut.Targetpath = python_exe
    shortcut.Arguments = f'"{script_path}"'
    shortcut.WorkingDirectory = os.path.dirname(script_path)
    shortcut.IconLocation = python_exe
    shortcut.save()
    
    print(f"Shortcut created at: {shortcut_path}")

if __name__ == '__main__':
    try:
        create_backup_shortcut()
        print("Desktop shortcut created successfully!")
    except Exception as e:
        print(f"Error creating shortcut: {e}")
        print("You may need to install pywin32: py -m pip install pywin32")
