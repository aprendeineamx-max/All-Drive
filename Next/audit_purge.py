import os
import json
from google.cloud import storage

# Context
CREDENTIALS = r'C:\Users\AzureAdmin\Desktop\All Drive\Legacy\Claves GCP\eastern-kit-482604-e0-dce887f8a438.json'
BUCKET_NAME = 'sincronizacion-automatica-de-vm-azureadmin-virtualbuk'
LOCAL_PATH = r'c:\Users\AzureAdmin\Desktop'
ROOT_FOLDER = 'Desktop'

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = CREDENTIALS

def audit_and_purge():
    client = storage.Client()
    bucket = client.bucket(BUCKET_NAME)
    
    print(f"Auditing bucket: {BUCKET_NAME} for root: {ROOT_FOLDER}")
    
    blobs = list(bucket.list_blobs(prefix=f"{ROOT_FOLDER}/"))
    count = 0
    purged = 0
    
    for blob in blobs:
        count += 1
        # Get path relative to the root folder (e.g. "file.txt" from "Desktop/file.txt")
        rel_path = blob.name[len(ROOT_FOLDER):].lstrip('/')
        
        if not rel_path:
            continue
            
        # Construct local path
        local_full = os.path.join(LOCAL_PATH, rel_path.replace('/', os.sep))
        
        if not os.path.exists(local_full):
            print(f"Ghost detected: {blob.name}")
            try:
                # Check for sub-blobs if it's a "folder" (common in GCS)
                # But since we are iterating all blobs, we just delete this one
                blob.delete()
                print(f"SUCCESS: Purged {blob.name}")
                purged += 1
            except Exception as e:
                print(f"FAILED: Could not purge {blob.name}: {str(e)}")

    print(f"Audit complete. Processed {count} items, purged {purged} ghosts.")

if __name__ == "__main__":
    audit_and_purge()
