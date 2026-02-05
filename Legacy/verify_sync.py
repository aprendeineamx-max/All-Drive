
import os
import json
from google.cloud import storage

CRED_PATH = r"c:\Users\AzureAdmin\Desktop\All Drive\Legacy\Claves GCP\eastern-kit-482604-e0-dce887f8a438.json"
BUCKET_NAME = "sincronizacion-automatica-de-vm-azureadmin-virtualbuk"

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = CRED_PATH

client = storage.Client()
bucket = client.bucket(BUCKET_NAME)
blobs = list(bucket.list_blobs(max_results=10))

print(f"--- BUCKET VERIFICATION: {BUCKET_NAME} ---")
if not blobs:
    print("El bucket está vacío actualmente.")
else:
    print("Últimos archivos subidos:")
    for b in blobs:
        print(f"📄 {b.name} ({b.size} bytes)")
