import os
import sys
from sqlalchemy import create_engine, text
from ev_shared.config import Settings

def check_schema():
    # Use the same logic as repositories.py to connect to ev_paquetes
    paq_user = os.getenv('PAQUETES_DB_USER', os.getenv('app_paquetes_user', 'app_paquetes'))
    paq_pass = os.getenv('PAQUETES_DB_PASS', os.getenv('app_paquetes_pass', 'Pkg_2025'))
    paq_host = os.getenv('PAQUETES_DB_HOST', os.getenv('DB_HOST', 'localhost'))
    paq_port = int(os.getenv('PAQUETES_DB_PORT', os.getenv('DB_PORT', '3306')))
    paq_db = os.getenv('PAQUETES_DB_NAME', 'ev_paquetes')
    
    engine_url = f"mysql+pymysql://{paq_user}:{paq_pass}@{paq_host}:{paq_port}/{paq_db}"
    print(f"Connecting to {engine_url} ...")
    
    engine = create_engine(engine_url)
    try:
        with engine.connect() as conn:
            result = conn.execute(text("DESCRIBE paquete")).mappings().all()
            print("Table 'paquete' columns:")
            found_desc = False
            for row in result:
                print(f"- {row['Field']} ({row['Type']})")
                if row['Field'] == 'descripcion':
                    found_desc = True
            
            if found_desc:
                print("\nSUCCESS: 'descripcion' column exists.")
            else:
                print("\nFAILURE: 'descripcion' column MISSING.")
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_schema()
