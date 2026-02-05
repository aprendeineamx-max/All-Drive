import os
import glob
from google.cloud import storage
import sys

def test_gcp():
    print("Buscando credenciales...")
    key_dir = os.path.join(os.getcwd(), "Claves GCP")
    if not os.path.exists(key_dir):
        print(f"Directorio no encontrado: {key_dir}")
        return

    json_files = glob.glob(os.path.join(key_dir, "*.json"))
    if not json_files:
        print("No se encontraron archivos JSON.")
        return

    key_path = json_files[0]
    print(f"Usando credencial: {key_path}")
    
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = key_path
    
    try:
        print("Inicializando cliente...")
        client = storage.Client()
        print(f"Cliente inicializado. Proyecto: {client.project}")
        
        print("Listando buckets...")
        buckets = list(client.list_buckets(max_results=5))
        print(f"Encontrados {len(buckets)} buckets.")
        for b in buckets:
            print(f" - {b.name}")
            
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_gcp()
