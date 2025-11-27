from pathlib import Path
import sys
import os

# Ensure tests can import the shared library `ev_shared` located at
# <repo-root>/libs/shared/ev_shared by adding <repo-root>/libs/shared to sys.path.
# This file is intentionally simple and safe for local and CI usage.

HERE = Path(__file__).resolve()
# services/iam-service/test -> parents[0]=test,1=iam-service,2=services,3=repo-root
repo_root = HERE.parents[3]
shared_dir = repo_root / "libs" / "shared"

if shared_dir.exists():
    sp = str(shared_dir)
    if sp not in sys.path:
        sys.path.insert(0, sp)

# Load service .env into environment for tests so BaseSettings finds DB credentials
# This allows running pytest from repo root while services expect their own .env
service_dir = HERE.parents[1]
env_file = service_dir / '.env'
if env_file.exists():
    try:
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if '=' not in line:
                    continue
                key, val = line.split('=', 1)
                key = key.strip()
                val = val.strip().strip('"').strip("'")
                # Don't overwrite existing env vars set by CI or user unless absent
                if key not in os.environ:
                    os.environ[key] = val
    except Exception:
        pass
