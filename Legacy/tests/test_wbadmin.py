import subprocess
import sys
import ctypes

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def check_wbadmin():
    print("--- Verifying wbadmin Availability ---")
    
    if not is_admin():
        print("❌ ERROR: Access denied. Must run as Administrator to use wbadmin.")
        return

    try:
        # Check if wbadmin is in path and get versions info
        print("Running: wbadmin get versions")
        result = subprocess.run(
            ["wbadmin", "get", "versions"], 
            capture_output=True, 
            text=True
        )
        
        print(f"Return Code: {result.returncode}")
        if result.returncode == 0:
            print("✅ wbadmin is available and working.")
            print("Output:")
            print(result.stdout)
        else:
            print("⚠️ wbadmin returned an error (expected if no backups configured yet).")
            print("Stderr:")
            print(result.stderr)
            
            if "'wbadmin' is not recognized" in result.stderr:
                print("❌ CRITICAL: wbadmin tool not found. Windows Server Backup feature might be missing.")

                print("\nAttempting to check status via PowerShell...")
                ps_result = subprocess.run(
                    ["powershell", "-Command", "Get-WindowsFeature -Name Windows-Server-Backup"],
                    capture_output=True,
                    text=True
                )
                print(ps_result.stdout)

    except FileNotFoundError:
        print("❌ CRITICAL: wbadmin executable not found in PATH.")
    except Exception as e:
        print(f"❌ UNEXPECTED ERROR: {e}")

if __name__ == "__main__":
    check_wbadmin()
