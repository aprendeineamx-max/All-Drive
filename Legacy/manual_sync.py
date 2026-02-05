
import os
import sys
import json
import time

# Setup paths
CRED_PATH = r"c:\Users\AzureAdmin\Desktop\All Drive\Legacy\Claves GCP\eastern-kit-482604-e0-dce887f8a438.json"
BUCKET_NAME = "sincronizacion-automatica-de-vm-azureadmin-virtualbuk"
USER_DESKTOP = r"c:\Users\AzureAdmin\Desktop"

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = CRED_PATH

print(f"[MANUAL ACTION] Starting Sync as 'Agente Humano'...")
print(f"Credentials: {os.path.basename(CRED_PATH)}")
print(f"Target Bucket: {BUCKET_NAME}")
print(f"Source: {USER_DESKTOP}")

try:
    from google.cloud import storage
    from file_watcher import RealTimeSync

    class HelperAdapter:
        def __init__(self):
            self.client = storage.Client()
        def upload_file(self, bucket_name, file_path, object_name=None):
            try:
                bucket = self.client.bucket(bucket_name)
                blob = bucket.blob(object_name or file_path)
                blob.upload_from_filename(file_path)
                print(f"[UPLOAD OK] {os.path.basename(file_path)}")
                return True
            except Exception as e:
                print(f"[UPLOAD ERROR] {str(e)}")
                return False

    def on_log(msg):
        print(f"[WATCHDOG] {msg}")

    adapter = HelperAdapter()
    
    # Initialize Sync
    sync = RealTimeSync(adapter, BUCKET_NAME, USER_DESKTOP, callback=on_log)
    
    success, msg = sync.start()
    
    if success:
        print(f"✓ Sincronización ACTIVA: {msg}")
        print("Manteniendo proceso vivo... (Presiona Ctrl+C para detener)")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            sync.stop()
            print("Sync detenida manualmente.")
    else:
        print(f"✗ Falló el inicio: {msg}")

except Exception as e:
    print(f"CRITICAL ERROR: {str(e)}")
