import requests
import json

CATALOGO_URL = "http://localhost:8020"

def check_catalogo_response():
    print("Checking Catalogo Service response for 'opcion_id'...")
    try:
        # Assuming endpoint is /catalogo/v1/servicios or /v1/servicios depending on how it's mounted
        # Based on previous files, it seems to be /catalogo/v1/servicios or similar.
        # Let's try to list services.
        
        # Try direct service URL
        url = f"{CATALOGO_URL}/catalogo/v1/servicios"
        print(f"GET {url}")
        resp = requests.get(url)
        
        if resp.status_code == 404:
             url = f"{CATALOGO_URL}/v1/servicios"
             print(f"GET {url}")
             resp = requests.get(url)
        
        print(f"Status: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            if isinstance(data, dict) and 'items' in data:
                items = data['items']
            elif isinstance(data, list):
                items = data
            else:
                items = []
            
            if items:
                first = items[0]
                print("First service item keys:", first.keys())
                if 'opcion_id' in first:
                    print(f"SUCCESS: 'opcion_id' found: {first['opcion_id']}")
                else:
                    print("FAILURE: 'opcion_id' NOT found in response.")
                    print("Sample item:", json.dumps(first, indent=2))
            else:
                print("No services found.")
        else:
            print(f"Error: {resp.text}")

    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    check_catalogo_response()
