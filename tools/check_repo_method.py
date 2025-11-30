
import sys
import os

# Add the service directory to sys.path (FIX: repo-relative path)
from pathlib import Path
REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(REPO_ROOT / 'services' / 'catalogo-service'))

try:
    from app.infrastructure.db.repositories import MySQLCatalogoCommandRepository
    repo = MySQLCatalogoCommandRepository()
    print(f"Has delete_paquete: {hasattr(repo, 'delete_paquete')}")
    if hasattr(repo, 'delete_paquete'):
        print("delete_paquete method found.")
    else:
        print("delete_paquete method NOT found.")
except Exception as e:
    print(f"Error importing repository: {e}")
