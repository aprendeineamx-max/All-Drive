
import os
import glob
from google.cloud import storage

def fix_duplicates():
    key_dir = os.path.join(os.getcwd(), "Claves GCP")
    json_files = glob.glob(os.path.join(key_dir, "*.json"))
    key_path = json_files[0]
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = key_path
    
    storage_client = storage.Client()
    buckets = list(storage_client.list_buckets())
    
    print("Buckets encontrados:")
    respaldo_buckets = []
    for b in buckets:
        print(f"- {b.name}")
        if b.name.startswith("respaldo-"):
            respaldo_buckets.append(b)
            
    # Logic: Keep the one with project_id (longer/specific) or just the first one?
    # The 'good' one is likely 'respaldo-eastern-kit-482604-e0'
    # The 'bad' one is likely 'respaldo-[random]'
    
    target_name = f"respaldo-{storage_client.project}"
    
    for b in respaldo_buckets:
        if b.name != target_name and "respaldo-" in b.name:
            print(f"Eliminando duplicado: {b.name}")
            try:
                b.delete()
                print("✅ Duplicado eliminado.")
            except Exception as e:
                print(f"❌ Error al eliminar: {e}")

if __name__ == "__main__":
    fix_duplicates()
