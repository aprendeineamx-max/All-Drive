
try:
    print("Attempting to import google.cloud.storage...")
    from google.cloud import storage
    print("Success: google.cloud.storage")
except Exception as e:
    print(f"Error importing google.cloud.storage: {e}")

try:
    print("Attempting to import ui.gcp_tab...")
    from ui.gcp_tab import GCPTab
    print("Success: ui.gcp_tab")
except Exception as e:
    print(f"Error importing ui.gcp_tab: {e}")
