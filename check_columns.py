import os
from sqlalchemy import create_engine, text

def check_columns():
    db_user = os.getenv('DB_USER', 'app_catalogo')
    db_pass = os.getenv('DB_PASS', 'Cat_2025')
    db_host = os.getenv('DB_HOST', 'localhost')
    db_port = int(os.getenv('DB_PORT', '3306'))
    db_name = os.getenv('DB_NAME', 'ev_catalogo')
    engine_url = f"mysql+pymysql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
    engine = create_engine(engine_url)

    with engine.connect() as conn:
        print("--- Columns in ev_catalogo.opcion_servicio ---")
        rows = conn.execute(text("DESCRIBE opcion_servicio")).fetchall()
        for r in rows:
            print(f"{r[0]} - {r[1]}")

if __name__ == "__main__":
    check_columns()
