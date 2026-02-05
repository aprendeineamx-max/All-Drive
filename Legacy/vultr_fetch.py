import requests
import json
import sys

API_KEY = "TO5MI6UX2KIIMWIBIWBSS5XKFXO5YFDJGOAQ"
URL = "https://api.vultr.com/v2/object-storage"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

try:
    response = requests.get(URL, headers=headers)
    response.raise_for_status()
    data = response.json()
    
    if 'object_storages' in data and len(data['object_storages']) > 0:
        # Assuming we want the first one or we list them all
        # For this user, let's try to find the best match or just list valid ones
        print(json.dumps(data, indent=2))
        
        # Save credentials to a file for the next steps so we don't have to parse stdout manually if it's complex
        with open("vultr_creds.json", "w") as f:
            json.dump(data, f, indent=2)
            
    else:
        print("No object storages found.")
        sys.exit(1)

except Exception as e:
    print(f"Error fetching data: {e}")
    sys.exit(1)
