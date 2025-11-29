import sys
import os
from sqlalchemy import text

# Add the service root to sys.path
service_root = os.path.abspath(os.path.dirname(__file__))
sys.path.append(service_root)

# Add shared lib to sys.path
shared_lib_path = os.path.abspath(os.path.join(service_root, '../../libs/shared'))
sys.path.append(shared_lib_path)

from app.entrypoints.fastapi.dependencies import get_settings, get_db_session

def update_schema():
    print(f"Service Root: {service_root}")
    print(f"Shared Lib Path: {shared_lib_path}")
    
    try:
        settings = get_settings()
        print(f"Connecting to DB: {settings.database_url}")
        
        # Get a session generator
        session_gen = get_db_session(settings)
        session = next(session_gen)
        
        try:
            # Check if column exists
            print("Checking if 'num_personas' exists in 'ev_contratacion.pedido_evento'...")
            result = session.execute(text("""
                SELECT COUNT(*) 
                FROM information_schema.columns 
                WHERE table_schema = 'ev_contratacion' 
                AND table_name = 'pedido_evento' 
                AND column_name = 'num_personas'
            """))
            exists = result.scalar()
            
            if exists:
                print("Column 'num_personas' already exists.")
            else:
                print("Adding 'num_personas' column...")
                session.execute(text("""
                    ALTER TABLE ev_contratacion.pedido_evento 
                    ADD COLUMN num_personas INT NOT NULL DEFAULT 1 AFTER hora_fin
                """))
                session.commit()
                print("Column added successfully.")
                
        except Exception as e:
            print(f"Error updating schema: {e}")
            session.rollback()
        finally:
            session.close()
            
    except Exception as e:
        print(f"Initialization Error: {e}")

if __name__ == "__main__":
    update_schema()
