import os
from sqlalchemy import create_engine, text

def check_prices():
    paq_user = os.getenv('PAQUETES_DB_USER', 'app_paquetes')
    paq_pass = os.getenv('PAQUETES_DB_PASS', 'Pkg_2025')
    paq_host = os.getenv('PAQUETES_DB_HOST', 'localhost')
    paq_port = int(os.getenv('PAQUETES_DB_PORT', '3306'))
    paq_db = os.getenv('PAQUETES_DB_NAME', 'ev_paquetes')
    engine_url = f"mysql+pymysql://{paq_user}:{paq_pass}@{paq_host}:{paq_port}/{paq_db}"
    engine = create_engine(engine_url)

    with engine.connect() as conn:
        print("--- Paquetes ---")
        rows = conn.execute(text("SELECT id, nombre FROM paquete")).fetchall()
        for r in rows:
            print(f"Paquete: {r.nombre} ({r.id})")
            prices = conn.execute(text("SELECT * FROM precio_paquete WHERE paquete_id = :pid"), {"pid": r.id}).fetchall()
            if not prices:
                print("  -> NO PRICE FOUND")
            else:
                for p in prices:
                    print(f"  -> Price: {p.monto} {p.moneda} (Desde: {p.vigente_desde})")

if __name__ == "__main__":
    check_prices()
