"""
Vultr Drive Desktop - Setup and Configuration Helper
This script helps set up the application for first-time use
"""

import os
import sys
import subprocess

def check_dependencies():
    """Check if all required dependencies are installed"""
    print("Checking dependencies...")
    
    dependencies = ['PyQt6', 'boto3', 'watchdog', 'pywin32']
    missing = []
    
    for dep in dependencies:
        try:
            __import__(dep.lower().replace('-', '_'))
            print(f"  ✓ {dep} is installed")
        except ImportError:
            print(f"  ✗ {dep} is NOT installed")
            missing.append(dep)
    
    return missing

def install_dependencies(missing):
    """Install missing dependencies"""
    if not missing:
        print("\n✓ All dependencies are already installed!")
        return True
    
    print(f"\nInstalling missing dependencies: {', '.join(missing)}")
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + missing)
        print("\n✓ Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError:
        print("\n✗ Error installing dependencies")
        return False

def check_rclone():
    """Check if rclone.exe exists"""
    rclone_path = os.path.join(os.path.dirname(__file__), 'rclone.exe')
    if os.path.exists(rclone_path):
        print("\n✓ rclone.exe found")
        return True
    else:
        print("\n✗ rclone.exe not found")
        print("  Please run this script from the VultrDriveDesktop directory")
        return False

def create_desktop_shortcut():
    """Create a desktop shortcut for the application"""
    try:
        import winshell
        from win32com.client import Dispatch
        
        desktop = winshell.desktop()
        python_exe = sys.executable.replace('python.exe', 'pythonw.exe')
        if not os.path.exists(python_exe):
            python_exe = sys.executable
        
        script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app.py")
        shortcut_path = os.path.join(desktop, "Vultr Drive Desktop.lnk")
        
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(shortcut_path)
        shortcut.Targetpath = python_exe
        shortcut.Arguments = f'"{script_path}"'
        shortcut.WorkingDirectory = os.path.dirname(script_path)
        shortcut.IconLocation = python_exe
        shortcut.save()
        
        print(f"\n✓ Desktop shortcut created: {shortcut_path}")
        return True
    except Exception as e:
        print(f"\n✗ Error creating desktop shortcut: {e}")
        return False

def create_backup_shortcut():
    """Create a desktop shortcut for quick backup"""
    try:
        import winshell
        from win32com.client import Dispatch
        
        desktop = winshell.desktop()
        python_exe = sys.executable.replace('python.exe', 'pythonw.exe')
        if not os.path.exists(python_exe):
            python_exe = sys.executable
        
        script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backup_now.py")
        shortcut_path = os.path.join(desktop, "Vultr Backup Now.lnk")
        
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(shortcut_path)
        shortcut.Targetpath = python_exe
        shortcut.Arguments = f'"{script_path}"'
        shortcut.WorkingDirectory = os.path.dirname(script_path)
        shortcut.IconLocation = python_exe
        shortcut.save()
        
        print(f"✓ Backup shortcut created: {shortcut_path}")
        return True
    except Exception as e:
        print(f"✗ Error creating backup shortcut: {e}")
        return False

def main():
    print("=" * 60)
    print("  Vultr Drive Desktop - Setup Wizard")
    print("=" * 60)
    print()
    
    # Check dependencies
    missing = check_dependencies()
    
    # Install missing dependencies
    if missing:
        response = input("\nDo you want to install missing dependencies? (y/n): ")
        if response.lower() == 'y':
            if not install_dependencies(missing):
                print("\nSetup failed. Please install dependencies manually.")
                return
        else:
            print("\nSetup cancelled.")
            return
    
    # Check rclone
    if not check_rclone():
        print("\nSetup incomplete. Please ensure you're in the correct directory.")
        return
    
    # Create shortcuts
    print("\n" + "=" * 60)
    print("  Creating Desktop Shortcuts")
    print("=" * 60)
    
    response = input("\nCreate desktop shortcut for Vultr Drive Desktop? (y/n): ")
    if response.lower() == 'y':
        create_desktop_shortcut()
    
    response = input("\nCreate desktop shortcut for Quick Backup? (y/n): ")
    if response.lower() == 'y':
        create_backup_shortcut()
    
    print("\n" + "=" * 60)
    print("  Setup Complete!")
    print("=" * 60)
    print("\nYou can now run the application by:")
    print("  1. Double-clicking 'Vultr Drive Desktop' on your desktop")
    print("  2. Running: py app.py")
    print("\nFor quick backups, use the 'Vultr Backup Now' shortcut")
    print("\nEnjoy using Vultr Drive Desktop!")
    print()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nSetup cancelled by user.")
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
    
    input("\nPress Enter to exit...")
