
import os
import uuid
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load env vars
load_dotenv('e:\\eventos-peru-hexagonal\\services\\catalogo-service\\.env')

def debug_delete():
    paquete_id = "7802e8e9-52c5-4156-824d-b2c6f2905c80" # ID from the user's error log
    
    paq_user = os.getenv('PAQUETES_DB_USER', 'app_paquetes')
    paq_pass = os.getenv('PAQUETES_DB_PASS', 'Pkg_2025')
    paq_host = os.getenv('PAQUETES_DB_HOST', 'localhost')
    paq_port = int(os.getenv('PAQUETES_DB_PORT', '3306'))
    paq_db = os.getenv('PAQUETES_DB_NAME', 'ev_paquetes')
    
    engine_url = f"mysql+pymysql://{paq_user}:{paq_pass}@{paq_host}:{paq_port}/{paq_db}"
    print(f"Connecting to {engine_url.replace(paq_pass, '***')}")
    
    engine = create_engine(engine_url)
    
    try:
        with engine.begin() as conn:
            print(f"Attempting DELETE (soft) for package {paquete_id}...")
            result = conn.execute(text("UPDATE ev_paquetes.paquete SET is_deleted = 1, updated_at = NOW() WHERE id = :id"), {"id": paquete_id})
            print(f"Rows affected: {result.rowcount}")
            print("DELETE successful.")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        engine.dispose()

if __name__ == "__main__":
    debug_delete()
