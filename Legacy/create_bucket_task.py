
import os
import glob
from google.cloud import storage
import random
import string

def create_bucket():
    # 1. Buscar credenciales
    key_dir = os.path.join(os.getcwd(), "Claves GCP")
    json_files = glob.glob(os.path.join(key_dir, "*.json"))
    
    if not json_files:
        print("Error: No se encontraron credenciales en 'Claves GCP'")
        return

    key_path = json_files[0]
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = key_path
    
    try:
        storage_client = storage.Client()
        project_id = storage_client.project
        
        # Generar nombre único basado en "Respaldo"
        # Los nombres de bucket son globales, así que "Respaldo" seguro está tomado.
        # Usaremos "respaldo-[project_id]" o similar.
        bucket_name = f"respaldo-{project_id}"
        
        print(f"Intentando crear bucket: {bucket_name}")
        print("Nota: En GCP el almacenamiento es elástico, no es necesario reservar 1 TB previamente.")
        
        bucket = storage_client.create_bucket(bucket_name, location="US")
        print(f"✅ Bucket creado exitosamente: {bucket.name}")
        print(f"   Ubicación: {bucket.location}")
        print(f"   Almacenamiento: Automático (Escala hasta exabytes)")

    except Exception as e:
        print(f"❌ Error al crear bucket: {e}")
        # Si falla por nombre, intentamos uno aleatorio
        try:
            suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
            bucket_name_alt = f"respaldo-{suffix}"
            print(f"Intentando con nombre alternativo: {bucket_name_alt}")
            bucket = storage_client.create_bucket(bucket_name_alt, location="US")
            print(f"✅ Bucket creado exitosamente: {bucket.name}")
        except Exception as e2:
             print(f"❌ Error final: {e2}")

if __name__ == "__main__":
    create_bucket()
