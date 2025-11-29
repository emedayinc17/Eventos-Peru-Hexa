import os
from dotenv import load_dotenv

def check_secrets():
    services = {
        "iam": "services/iam-service/.env",
        "catalogo": "services/catalogo-service/.env",
        "proveedores": "services/proveedores-service/.env"
    }
    
    for name, path in services.items():
        full_path = os.path.join(os.getcwd(), path)
        if os.path.exists(full_path):
            # Clear env vars to ensure we read from file
            if "JWT_SECRET" in os.environ:
                del os.environ["JWT_SECRET"]
            
            load_dotenv(full_path)
            secret = os.getenv("JWT_SECRET")
            print(f"{name}: {secret}")
        else:
            print(f"{name}: .env not found at {full_path}")

if __name__ == "__main__":
    check_secrets()
