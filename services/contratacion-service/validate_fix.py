import sys
import os
import traceback

# Add services dir to path
current_dir = os.path.dirname(os.path.abspath(__file__))
services_dir = os.path.dirname(current_dir)
root_dir = os.path.dirname(services_dir)
libs_shared_dir = os.path.join(root_dir, "libs", "shared")
sys.path.append(services_dir)
sys.path.append(libs_shared_dir)

try:
    from ev_shared.config import load_settings
    from app.entrypoints.fastapi.dependencies import get_listar_pedidos_admin_use_case
    from app.infrastructure.db.repositories import MySQLPedidoRepository
    from app.infrastructure.http.iam_client import IamClient
    from app.infrastructure.http.catalogo_client import CatalogoClient
except ImportError as e:
    print(f"Import Error: {e}")
    sys.exit(1)

def validate():
    print("--- Validating Fix ---")
    
    print("1. Loading Settings...")
    try:
        settings = load_settings(service_name="contratacion-service")
        print("   Settings loaded.")
        
        # Check for IAM_SERVICE_URL
        if hasattr(settings, "IAM_SERVICE_URL"):
            print(f"   IAM_SERVICE_URL: {settings.IAM_SERVICE_URL}")
        else:
            print("   ERROR: IAM_SERVICE_URL not found in Settings!")
            # This might be the cause, but let's continue to see if it crashes
            
    except Exception as e:
        print(f"   Error loading settings: {e}")
        return

    print("\n2. Initializing Dependencies...")
    try:
        repo = MySQLPedidoRepository()
        iam_client = IamClient(settings)
        catalogo_client = CatalogoClient(settings)
        print("   Dependencies initialized.")
    except Exception as e:
        print(f"   Error initializing dependencies: {e}")
        traceback.print_exc()
        return

    print("\n3. Creating Use Case...")
    try:
        use_case = get_listar_pedidos_admin_use_case(
            pedido_repo=repo,
            iam_client=iam_client,
            catalogo_client=catalogo_client
        )
        print("   Use Case created.")
    except Exception as e:
        print(f"   Error creating use case: {e}")
        traceback.print_exc()
        return

    print("\n4. Executing Use Case (Dry Run)...")
    try:
        # We need a db session. 
        from ev_shared.db import session_scope
        with session_scope(settings) as session:
            # Pass a dummy token or None
            pedidos = use_case.execute(session, limit=5, auth_token="dummy_token")
            print(f"   Success! Retrieved {len(pedidos)} orders.")
            
            if pedidos:
                p = pedidos[0]
                print(f"   Sample Order ID: {p.id}")
                print(f"   Cliente: {p.cliente_nombre} ({p.cliente_email})")
                print(f"   Evento: {p.tipo_evento_nombre}")
                
    except Exception as e:
        print(f"   Error executing use case: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    validate()
