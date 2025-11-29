import os
from sqlalchemy import create_engine, text

def check_package_price():
    paq_user = os.getenv('PAQUETES_DB_USER', 'app_paquetes')
    paq_pass = os.getenv('PAQUETES_DB_PASS', 'Pkg_2025')
    paq_host = os.getenv('PAQUETES_DB_HOST', 'localhost')
    paq_port = int(os.getenv('PAQUETES_DB_PORT', '3306'))
    paq_db = os.getenv('PAQUETES_DB_NAME', 'ev_paquetes')
    engine_url = f"mysql+pymysql://{paq_user}:{paq_pass}@{paq_host}:{paq_port}/{paq_db}"
    engine = create_engine(engine_url)

    with engine.connect() as conn:
        print("--- Checking Prices for 'Paquete Concierto Estándar' ---")
        # Find ID
        rows = conn.execute(text("SELECT id, nombre FROM paquete WHERE nombre LIKE '%Concierto Estándar%'")).fetchall()
        for r in rows:
            print(f"Paquete: {r.nombre} ({r.id})")
            prices = conn.execute(text("SELECT * FROM precio_paquete WHERE paquete_id = :pid ORDER BY vigente_desde DESC, created_at DESC"), {"pid": r.id}).fetchall()
            for p in prices:
                print(f"  -> Price: {p.monto} {p.moneda} (Desde: {p.vigente_desde}, Created: {p.created_at})")

if __name__ == "__main__":
    check_package_price()
