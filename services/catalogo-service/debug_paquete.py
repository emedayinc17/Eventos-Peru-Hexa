import os
import sys
import logging
from sqlalchemy import create_engine, text
from app.infrastructure.db.repositories import MySQLCatalogoCommandRepository
from ev_shared.config import Settings
from ev_shared.db import session_scope

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def debug_create_paquete():
    settings = Settings()
    repo = MySQLCatalogoCommandRepository()
    
    # 1. Get a valid opcion_servicio_id
    with session_scope(settings) as session:
        result = session.execute(text("SELECT id FROM ev_catalogo.opcion_servicio LIMIT 1")).mappings().first()
        if not result:
            print("No options found in DB")
            return
        opcion_id = result['id']
        print(f"Using opcion_id: {opcion_id}")

        # 2. Try to create a package
        try:
            print("Attempting to create package...")
            # Mock session is not used by create_paquete for the main insert, but passed as arg
            # create_paquete uses its own engine connection
            
            # Generate a code
            import uuid
            codigo = f"PKG-TEST-{str(uuid.uuid4())[:8]}"
            
            result = repo.create_paquete(
                session, 
                codigo=codigo, 
                nombre="Paquete Test Debug", 
                descripcion="",
                items=[{"opcion_servicio_id": opcion_id, "cantidad": 1}],
                moneda="PEN"
            )
            print("Success!")
            print(result)
        except Exception as e:
            print("FAILED!")
            print(e)
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    # Ensure we are in the right directory for imports to work
    sys.path.append(os.getcwd())
    debug_create_paquete()
