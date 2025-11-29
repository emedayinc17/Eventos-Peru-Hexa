import os
from sqlalchemy import create_engine, text
from decimal import Decimal

def recalculate_prices():
    # DB Connections
    cat_user = os.getenv('DB_USER', 'app_catalogo')
    cat_pass = os.getenv('DB_PASS', 'Catalogo_2025')
    cat_host = os.getenv('DB_HOST', 'localhost')
    cat_port = int(os.getenv('DB_PORT', '3306'))
    cat_db = os.getenv('DB_NAME', 'ev_catalogo')
    cat_url = f"mysql+pymysql://{cat_user}:{cat_pass}@{cat_host}:{cat_port}/{cat_db}"
    cat_engine = create_engine(cat_url)

    paq_user = os.getenv('PAQUETES_DB_USER', 'app_paquetes')
    paq_pass = os.getenv('PAQUETES_DB_PASS', 'Pkg_2025')
    paq_host = os.getenv('PAQUETES_DB_HOST', 'localhost')
    paq_port = int(os.getenv('PAQUETES_DB_PORT', '3306'))
    paq_db = os.getenv('PAQUETES_DB_NAME', 'ev_paquetes')
    paq_url = f"mysql+pymysql://{paq_user}:{paq_pass}@{paq_host}:{paq_port}/{paq_db}"
    paq_engine = create_engine(paq_url)

    print("--- Recalculating Package Prices ---")

    with paq_engine.connect() as paq_conn:
        # Get all packages
        packages = paq_conn.execute(text("SELECT id, nombre FROM paquete WHERE is_deleted = 0")).fetchall()
        
        for pkg in packages:
            print(f"Processing {pkg.nombre} ({pkg.id})...")
            
            # Get items
            items = paq_conn.execute(text("SELECT opcion_servicio_id, cantidad FROM item_paquete WHERE paquete_id = :pid"), {"pid": pkg.id}).fetchall()
            
            total_price = Decimal(0)
            currency = 'PEN'
            
            if not items:
                print("  -> No items found.")
                continue

            with cat_engine.connect() as cat_conn:
                for item in items:
                    # Get latest price for option
                    # We use a loose date check to ensure we find a price
                    price_row = cat_conn.execute(text("""
                        SELECT monto, moneda 
                        FROM precio_servicio 
                        WHERE opcion_servicio_id = :oid 
                        ORDER BY vigente_desde DESC, created_at DESC 
                        LIMIT 1
                    """), {"oid": item.opcion_servicio_id}).fetchone()
                    
                    if price_row:
                        item_price = price_row.monto
                        qty = item.cantidad
                        total_price += item_price * qty
                        currency = price_row.moneda # Assume all same currency for now
                        print(f"  + Item {item.opcion_servicio_id}: {item_price} * {qty}")
                    else:
                        print(f"  ! No price found for option {item.opcion_servicio_id}")

            print(f"  = Calculated Total: {total_price} {currency}")

            # Update Package Price
            # Delete existing future/today prices to avoid conflicts
            paq_conn.execute(text("DELETE FROM precio_paquete WHERE paquete_id = :pid AND vigente_desde >= CURDATE()"), {"pid": pkg.id})
            
            # Insert new price
            import uuid
            paq_conn.execute(text("""
                INSERT INTO precio_paquete (id, paquete_id, moneda, monto, vigente_desde, created_at)
                VALUES (:id, :pid, :moneda, :monto, CURDATE(), NOW())
            """), {
                "id": str(uuid.uuid4()),
                "pid": pkg.id,
                "moneda": currency,
                "monto": total_price
            })
            paq_conn.commit()
            print("  -> Updated.")

if __name__ == "__main__":
    recalculate_prices()
