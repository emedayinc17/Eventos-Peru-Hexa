
import requests

def test_delete_direct():
    print("\nTesting DELETE via Service (8020)...")
    url = "http://localhost:8020/catalogo/v1/admin/paquetes/7802e8e9-52c5-4156-824d-b2c6f2905c80"
    print(f"URL: {url}")
    try:
        resp = requests.delete(url)
        print(f"Service Response: {resp.status_code}")
        print(resp.text)
    except Exception as e:
        print(f"Service Error: {e}")

if __name__ == "__main__":
    test_delete_direct()
