from pathlib import Path
import sys

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
